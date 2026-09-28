import sys
from PIL import ImageDraw
import utils

strokes = utils.read_strokes(sys.argv[1])
page = utils.draw_page(strokes)
draw = ImageDraw.Draw(page)

for row in range(utils.ROWS):
    top = utils.FIRST_ROW + row * utils.ROW_H
    draw.rectangle([utils.BOX_LEFT, top, utils.BOX_RIGHT, top + utils.BOX_H], outline="red")
    draw.line([utils.BOX_RIGHT + 70, top + 55, utils.PAGE_W, top + 55], fill="red")
    draw.text((20, top + 15), str(row), fill="red")

page.save("check.png")
print(len(strokes), "strokes, saved check.png")
