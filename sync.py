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
    if text == "":
        continue
    done = False
    for s in rows[row]:
        if utils.is_tick(s, row) or utils.is_strike(s):
            done = True
    # print(row, text, done)
    if text not in last:
        print("new:", text)
        add_task(text)
        last[text] = False
    if done and not last[text]:
        print("done:", text)
        last[text] = True

f = open("last_sync.json", "w")
json.dump(last, f, indent=2)
f.close()
