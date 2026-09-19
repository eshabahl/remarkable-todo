from rmscene import read_blocks, SceneLineItemBlock
from PIL import Image, ImageDraw
from ocrmac import ocrmac

f = open("test_pages/page1.rm", "rb")
strokes = []
for block in read_blocks(f):
    if isinstance(block, SceneLineItemBlock):
        # deleted strokes are still in the file but value is None
        if block.item.value is not None:
            points = []
            for p in block.item.value.points:
                # x is 0 in the middle of the page, not the left side
                points.append((p.x + 702, p.y))
            strokes.append(points)

print(len(strokes), "strokes")

img = Image.new("RGB", (1404, 1872), "white")
draw = ImageDraw.Draw(img)
for s in strokes:
    draw.line(s, fill="black", width=4)
img.save("page.png")

result = ocrmac.OCR("page.png").recognize()
print(result)
