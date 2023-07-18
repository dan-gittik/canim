from canim import code_animation, CodeScene


@code_animation
def remove_lines(scene: CodeScene):
    block = scene.create_code_block(-6, 3)
    line1, *_ = block.append_lines('''
        Line 1
        Line 2
        Line 3
        Line 4
        Line 5
        Line 6
    ''')
    line1.remove()
    block.lines[0:1, 3].remove()