from canim import code_animation, CodeScene


@code_animation(voiceover=True)
def with_voiceover(scene: CodeScene):
    block = scene.create_code_block(-6, 3)
    with scene.voiceover('''
        Its a simple idea: we bind a name to a value,{1} like x to 1;
        and when we reference the name,{2} x, it resolves to the value,{3} 1.
    '''):
        scene @ 1
        block.append_lines('>>> x = 1')
        scene @ 2
        block.append_lines('>>> x')
        scene @ 3
        block.append_lines('1')