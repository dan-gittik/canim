from canim import code_animation, CodeScene


@code_animation
def slide_down(scene: CodeScene):
    block = scene.create_code_block(-6, 3)
    block.append_lines('Line 1')
    line4, = block.append_lines('Line 4')
    line2, = line4.prepend_lines('Line 2')
    line3, = block.insert_lines(2, 'Line 3')
    block.prepend_lines('Line 0')