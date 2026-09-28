import sys
import utils

strokes = utils.read_strokes(sys.argv[1])
page = utils.draw_page(strokes)
rows = utils.find_rows(strokes)

for row in sorted(rows):
    text = utils.read_text(utils.row_image(page, row)).strip(" -")
    if text == "":
        continue
    done = False
    for s in rows[row]:
        if utils.is_tick(s, row) or utils.is_strike(s):
            done = True
    print(row, text, done)
