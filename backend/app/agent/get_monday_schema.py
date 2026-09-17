"""
Fetch a Monday.com board's full schema: columns (with IDs and types) and
groups (with IDs). Run this once to get everything needed for the n8n
workflow, then you can safely ignore/delete this script.

Usage:
    python get_monday_schema.py
"""
import requests

# --- EDIT THESE ---
API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjcwMjgxMzIzOCwiYWFpIjoxMSwidWlkIjoxMTU0OTI4ODUsImlhZCI6IjIwMjYtMDktMTFUMDU6MjI6MTIuMDAwWiIsInBlciI6Im1lOndyaXRlIiwiYWN0aWQiOjM2NzUxMjczLCJyZ24iOiJhcHNlMiJ9.FCicqCWDkVDx93pkLeyiP1vGD2qamGZ4_l5hnjkbVaI"
BOARD_ID = "5031241183"
# ------------------

query = """
query ($boardId: [ID!]) {
  boards(ids: $boardId) {
    id
    name
    columns {
      id
      title
      type
    }
    groups {
      id
      title
    }
  }
}
"""

response = requests.post(
    "https://api.monday.com/v2",
    json={"query": query, "variables": {"boardId": [BOARD_ID]}},
    headers={"Authorization": API_TOKEN, "Content-Type": "application/json"},
)

data = response.json()

if "errors" in data:
    print("ERROR:", data["errors"])
else:
    board = data["data"]["boards"][0]
    print(f"Board: {board['name']} (ID: {board['id']})\n")

    print("COLUMNS:")
    for col in board["columns"]:
        print(f"  {col['title']!r:30} id={col['id']!r:20} type={col['type']}")

    print("\nGROUPS:")
    for group in board["groups"]:
        print(f"  {group['title']!r:30} id={group['id']!r}")