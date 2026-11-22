import sys
import os
import json
import requests
from datetime import datetime, timedelta, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import utils

TODOIST = "https://api.todoist.com/api/v1"
# was calendar.readonly from the quickstart, had to change it to add events
# (and delete token.json so it asks again)
SCOPES = ["https://www.googleapis.com/auth/calendar"]
# was an environment variable but when the tablet runs this over ssh
# .zshrc isn't loaded so it wasn't there. todoist_token.txt is in .gitignore
f = open("todoist_token.txt")
HEADERS = {"Authorization": "Bearer " + f.read().strip()}
f.close()


def add_task(text):
    r = requests.post(TODOIST + "/tasks", headers=HEADERS, json={"content": text})
    r.raise_for_status()
    return r.json()["id"]


def close_task(task_id):
    r = requests.post(TODOIST + "/tasks/" + task_id + "/close", headers=HEADERS)
    r.raise_for_status()


# login part is from google's python quickstart
# invalid_grant = delete token.json and run it once on the mac.
# testing apps only get a 7 day login, published it in google cloud console
def calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def busy_today(service):
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=1)
    events = service.events().list(calendarId="primary", timeMin=now.isoformat(), timeMax=end.isoformat(),
                                   singleEvents=True, orderBy="startTime").execute()
    busy = []
    for e in events.get("items", []):
        # all day events only have a date, not a dateTime. skip them
        if "dateTime" not in e["start"]:
            continue
        start = datetime.fromisoformat(e["start"]["dateTime"])
        finish = datetime.fromisoformat(e["end"]["dateTime"])
        busy.append((start, finish))
    return busy


def block_time(service, text, start):
    end = start + timedelta(minutes=30)
    event = {
        "summary": text,
        "start": {"dateTime": start.isoformat()},
        "end": {"dateTime": end.isoformat()},
    }
    service.events().insert(calendarId="primary", body=event).execute()


strokes = utils.read_strokes(sys.argv[1])
page = utils.draw_page(strokes)
rows = utils.find_rows(strokes)

# what the page looked like last time
if os.path.exists("last_sync.json"):
    f = open("last_sync.json")
    last = json.load(f)
    f.close()
else:
    last = {}

service = calendar_service()
busy = busy_today(service)

for row in sorted(rows):
    text = utils.read_text(utils.row_image(page, row)).strip(" -")
    done = False
    for s in rows[row]:
        if utils.is_tick(s, row) or utils.is_strike(s):
            done = True
    # print(row, text, done)
    # the same row gets read a bit differently every time (and a line through
    # it changes the text) so use the row number, not the text
    key = str(row)  # json turns the keys into strings
    if key not in last:
        if text == "":
            continue
        print("new:", text)
        task_id = add_task(text)
        last[key] = {"text": text, "id": task_id, "done": False}
        slot = utils.next_free_slot(busy)
        if slot is None:
            print("  no time left today")
        else:
            block_time(service, text, slot)
            # so the next new task doesn't get the same time
            busy.append((slot, slot + timedelta(minutes=30)))
            print("  at", slot.strftime("%I:%M %p"))
    if done and not last[key]["done"]:
        print("done:", last[key]["text"])
        close_task(last[key]["id"])
        last[key]["done"] = True

f = open("last_sync.json", "w")
json.dump(last, f, indent=2)
f.close()
