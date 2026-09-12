from rmscene import read_blocks, SceneLineItemBlock

f = open("test_pages/page1.rm", "rb")
strokes = []
for block in read_blocks(f):
    if isinstance(block, SceneLineItemBlock):
        strokes.append(block.item.value)

print(len(strokes))
print(strokes[0])
