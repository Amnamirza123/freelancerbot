from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.config import settings
from app.agent.state import AgentState
from app.tools.tools import ALL_TOOLS
from app.prompts.prompts import MAIN_AGENT_PROMPT_V1, INTENT_CLASSIFICATION_PROMPT_V1


def _get_llm():
    if not settings.OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set in .env")

    return ChatOpenAI(
        model=settings.OPENROUTER_CHAT_MODEL,
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        temperature=0.3,
        timeout=30,
        max_retries=0,
        max_tokens=500,
    )


def understand_request(state: AgentState) -> AgentState:
    if not state["messages"]:
        return state

    last_message = state["messages"][-1].content

    llm = _get_llm()

    prompt = INTENT_CLASSIFICATION_PROMPT_V1.format(
        message=last_message
    )

    result = llm.invoke(prompt)

    intent = result.content.strip().lower()

    if intent not in {
        "pricing",
        "proposal",
        "meeting",
        "escalation",
        "general",
    }:
        intent = "general"

    return {
        **state,
        "detected_intent": intent,
    }


def decide_action(state: AgentState) -> AgentState:
    llm = _get_llm().bind_tools(ALL_TOOLS)

    system = {
        "role": "system",
        "content": MAIN_AGENT_PROMPT_V1,
    }

    response = llm.invoke(
        [
            system,
            *state["messages"],
        ]
    )

    return {
        **state,
        "messages": [*state["messages"], response],
    }


def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node(
        "decide_action",
        decide_action,
    )

    graph.add_node(
        "tools",
        ToolNode(ALL_TOOLS),
    )

    graph.add_edge(
        START,
        "decide_action",
    )

    graph.add_conditional_edges(
        "decide_action",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph.add_edge(
        "tools",
        "decide_action",
    )

    return graph.compile()


agent_graph = None


def get_agent_graph():
    global agent_graph

    if agent_graph is None:
        agent_graph = build_agent_graph()

    return agent_graph