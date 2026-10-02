import sys
import os
import json
import utils

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
        last[text] = False
    if done and not last[text]:
        print("done:", text)
        last[text] = True

f = open("last_sync.json", "w")
json.dump(last, f, indent=2)
f.close()
