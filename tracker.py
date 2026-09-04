import requests
import json
import os
from datetime import datetime, timezone

with open("watchlist.json") as f:
    USERNAMES = json.load(f)

URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0"
}

QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title
    timestamp
  }
  matchedUser(username: $username) {
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
}
"""

def fetch_user(username):
    variables = {"username": username, "limit": 20}
    resp = requests.post(URL, json={"query": QUERY, "variables": variables}, headers=HEADERS, timeout=10)
    data = resp.json()["data"]

    total = next(
        item["count"] for item in data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
        if item["difficulty"] == "All"
    )

    today = datetime.now(timezone.utc).date()
    solved_today_list = [
        sub["title"] for sub in data["recentAcSubmissionList"]
        if datetime.fromtimestamp(int(sub["timestamp"]), tz=timezone.utc).date() == today
    ]
    solved_today = list(dict.fromkeys(solved_today_list))

    return total, solved_today, len(solved_today)

def main():
    with open("records.json") as f:
        records = json.load(f)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for user in USERNAMES:
        try:
            total, solved_today, count_today = fetch_user(user)
        except Exception as e:
            print(f"Failed for {user}: {e}")
            continue

        records.setdefault(user, {})
        records[user][date_str] = {
            "total_solved": total,
            "count_today": count_today,
            "problems_today": solved_today
        }
        print(f"{user}: total={total}, today={count_today}")

    with open("records.json", "w") as f:
        json.dump(records, f, indent=2)

if __name__ == "__main__":
    main()
