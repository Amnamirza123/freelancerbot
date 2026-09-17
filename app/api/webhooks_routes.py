"""
Webhook receivers.

/webhooks/vapi   — Vapi calls this during/after a call:
                    - status-update (call started): create caller + call records + lead stub
                    - tool-calls (function-calling mode): caller's message goes to
                      our LangGraph agent, agent's answer goes back to Vapi to speak
                    - end-of-call-report: save transcript, clear session
/webhooks/n8n     — n8n calls this back after generating a post-call summary, and
                    updates the lead stub with real service/summary data.
"""

from fastapi import APIRouter, Request
from langchain_core.messages import HumanMessage

from app.services import callers as callers_service
from app.services import calls as calls_service


from app.agent.graph import get_agent_graph
from app.agent.state import AgentState
import httpx
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

_call_sessions: dict[str, AgentState] = {}


def _open_session(vapi_call_id: str, caller_phone: str | None) -> dict:
    caller = callers_service.get_or_create_caller(phone=caller_phone)
    call = calls_service.create_call(caller["id"], vapi_call_id)



    session = {
        "call_id": call["id"], "caller_id": caller["id"], "caller_name": None,
        "phone": caller_phone, "email": None, "messages": [], "detected_intent": None,
        "project_requirements": None, "assigned_developer": None,
        "preferred_meeting_times": None, "retrieved_context": None,
        "request_id": None, "request_status": None, "proposal_status": None,
        "escalation_status": None,
    }
    _call_sessions[vapi_call_id] = session
    return session


@router.post("/vapi")
async def vapi_webhook(request: Request):
    payload = await request.json()
    
    print("[VAPI PAYLOAD]", payload)

    message = payload.get("message", {})
    event_type = message.get("type") or payload.get("type")

    if event_type == "status-update" and payload.get("call", {}).get("status") == "in-progress":
        call_data = payload["call"]
        vapi_call_id = call_data.get("id")
        caller_phone = call_data.get("customer", {}).get("number")
        session = _open_session(vapi_call_id, caller_phone)
        return {"received": True, "call_id": session["call_id"], "caller_id": session["caller_id"]}

    if event_type == "tool-calls":
        vapi_call_id = payload.get("call", {}).get("id")
        tool_call_list = message.get("toolCallList", [])
        session = _call_sessions.get(vapi_call_id)

        if session is None:
            caller_phone = payload.get("call", {}).get("customer", {}).get("number")
            session = _open_session(vapi_call_id, caller_phone)

        results = []
        graph = get_agent_graph()

        for call in tool_call_list:
            tool_call_id = call.get("id")
            print(f"[VAPI DEBUG] raw tool call: {call}")
            args = call.get("function", {}).get("arguments", {})
            query = args.get("query") or args.get("message") or ""

            session["messages"].append(HumanMessage(content=query))

            import time
            _t0 = time.time()
            updated_state = graph.invoke(session)
            print(f"[VAPI DEBUG] agent took {time.time() - _t0:.2f}s")

            _call_sessions[vapi_call_id] = updated_state
            final_message = updated_state["messages"][-1]
            answer = getattr(final_message, "content", str(final_message))

            if not answer or not str(answer).strip():
                if "meeting" in query.lower() or "availability" in query.lower():
                    answer = ("I checked the requested time, but I couldn't get a complete "
                              "availability response. I don't want to guess about availability.")
                elif "human" in query.lower() or "representative" in query.lower() or "transfer" in query.lower():
                    answer = ("I wasn't able to complete the human escalation just yet, "
                              "so I don't want to tell you that it was completed when it wasn't.")
                else:
                    answer = "I wasn't able to complete that request right now. I don't want to give you an inaccurate answer."

            print(f"[VAPI DEBUG] query='{query}' -> answer='{answer}'")
            results.append({"toolCallId": tool_call_id, "result": answer})

        return {"results": results}

    if event_type == "end-of-call-report":
        call_data = payload.get("call", {})
        vapi_call_id = call_data.get("id")
        transcript = payload.get("transcript") or payload.get("artifact", {}).get("transcript")

        n8n_url = "https://amnaamir123.app.n8n.cloud/webhook/freelancerbot-vapi-webhook"

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                n8n_response = await client.post(n8n_url, json=payload)

            print(f"[N8N DEBUG] status={n8n_response.status_code}")
            print(f"[N8N DEBUG] response={n8n_response.text}")

        except Exception as e:
            print(f"[N8N ERROR] {e}")

        _call_sessions.pop(vapi_call_id, None)

        return {
            "received": True,
            "vapi_call_id": vapi_call_id,
            "transcript_length": len(transcript or ""),
        }


@router.post("/n8n")
async def n8n_webhook(request: Request):
    """n8n posts here after generating a call summary. Saves the summary AND fills
    in the lead stub (created at call start) with real service/description data."""
    payload = await request.json()

    vapi_call_id = payload.get("vapi_call_id")
    summary = payload.get("summary")
    interested_service = payload.get("interested_service")

    if not vapi_call_id:
        return {"stored": False, "error": "vapi_call_id is required"}

    call_result = calls_service.db().table("calls").select("id, caller_id").eq(
        "vapi_call_id", vapi_call_id
    ).execute()

    if not call_result.data:
        return {"stored": False, "error": f"No call found for vapi_call_id {vapi_call_id}"}

    call_row = call_result.data[0]
    internal_call_id = call_row["id"]
    caller_id = call_row["caller_id"]

    saved_summary = None
    if summary:
        saved_summary = calls_service.save_summary(internal_call_id, summary)

    # Update the lead stub created at call start with real data, most recent first.
    if caller_id:
        lead_result = calls_service.db().table("leads").select("id").eq(
            "caller_id", caller_id
        ).order("created_at", desc=True).limit(1).execute()
        if lead_result.data:
            calls_service.db().table("leads").update({
                "project_description": summary,
                "service": interested_service,
            }).eq("id", lead_result.data[0]["id"]).execute()

    return {"stored": True, "summary": saved_summary}