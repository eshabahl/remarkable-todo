from rmscene import read_blocks, SceneLineItemBlock
from PIL import Image, ImageDraw

# from the Checklist template file
FIRST_ROW = 257
ROW_H = 97.4
BOX_LEFT = 80
BOX_RIGHT = 135

f = open("test_pages/page1.rm", "rb")
page = Image.new("RGB", (1404, 1872), "white")
draw = ImageDraw.Draw(page)
for block in read_blocks(f):
    if isinstance(block, SceneLineItemBlock):
        if block.item.value is not None:
            points = []
            for p in block.item.value.points:
                points.append((p.x + 702, p.y))
            draw.line(points, fill="black", width=4)

for row in range(16):
    top = FIRST_ROW + row * ROW_H
    draw.rectangle([BOX_LEFT, top, BOX_RIGHT, top + 55], outline="red")
    draw.line([BOX_RIGHT + 70, top + 55, 1404, top + 55], fill="red")
    draw.text((20, top + 15), str(row), fill="red")

page.save("check.png")
