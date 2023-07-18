from canim import code_animation, CodeScene


@code_animation
def multiple_lines(scene: CodeScene):
    block = scene.create_code_block(-6, 3)
    block.append_lines('''
        Line 3
        Line 4
    ''')
    block.prepend_lines('''
        Line 1
        Line 2
    ''')