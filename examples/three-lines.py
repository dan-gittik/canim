from canim import code_animation, CodeScene


@code_animation
def three(scene: CodeScene):
    block = scene.create_code_block(-6, 3)
    block.append_line('Line 1')
    block.append_line('Line 2')
    block.append_line('Line 3')