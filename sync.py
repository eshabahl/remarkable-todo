import sys
import os
import json
import requests
import utils

TODOIST = "https://api.todoist.com/api/v1"
HEADERS = {"Authorization": "Bearer " + os.environ["TODOIST_TOKEN"]}


def add_task(text):
    r = requests.post(TODOIST + "/tasks", headers=HEADERS, json={"content": text})
    r.raise_for_status()
    return r.json()["id"]


def close_task(task_id):
    r = requests.post(TODOIST + "/tasks/" + task_id + "/close", headers=HEADERS)
    r.raise_for_status()


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
    if done and not last[key]["done"]:
        print("done:", last[key]["text"])
        close_task(last[key]["id"])
        last[key]["done"] = True

f = open("last_sync.json", "w")
json.dump(last, f, indent=2)
f.close()
