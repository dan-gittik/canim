from canim import code_animation, CodeScene


@code_animation
def slide_down(scene: CodeScene):
    block = scene.create_code_block(-6, 3)
    block.append_line('Line 1')
    line4 = block.append_line('Line 4')
    line2 = line4.prepend_line('Line 2')
    line3 = block.insert_line('Line 3', 2)
    block.prepend_line('Line 0')