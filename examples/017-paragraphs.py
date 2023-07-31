from canim import code_animation, CodeScene, themes


p1 = '''
This is a paragraph.
There are natural line breaks, but some lines are pretty long, and should be wrapped accordingly - not just once, but even several times if necessary.
'''.strip()

p2 = '''
This is a changed paragraph.
There are natural line breaks, but some lines are pretty long, and should be wrapped accordingly - not just once, but even several times if necessary.
'''.strip()


@code_animation
def example(scene: CodeScene):
    code = scene.code(small=True, theme=themes.Bauhaus())
    code >>= '''
    Line 1
    Line 2
    Line 3
    '''
    with code.title('Some long title'):
        scene.wait(1)
    code >>= '''
    Line 4
    Line 5
    '''
    with code.paragraph(p1) as paragraph:
        scene.wait(1)
        paragraph.change(p2)
        scene.wait(1)