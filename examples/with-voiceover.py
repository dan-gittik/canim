from canim import code_animation, CodeScene


@code_animation
def with_voiceover(scene: CodeScene):
    code = scene.code(voiceover=True)
    with code.voiceover('''
        Its a simple idea: we bind a name to a value,{1} like x to 1;
        and when we reference the name,{2} x, it resolves to the value,{3} 1.
    '''):
        code @ 1
        code >> '>>> x = 1'
        code @ 2
        code >> '>>> x'
        code @ 3
        code >> '1'