from canim import code_animation, CodeScene, themes


@code_animation
def example(scene: CodeScene):
    code = scene.code(small=True, theme=themes.Window())
    code >> '''
        Line 1
        Line 2
        Line 3
        Line 4
        Line 5
        Line 6
        Line 7
    '''
    code[1:3, 5] < '''
        New line 2
        New line 3
        New line 4
    '''
    code[1:3, 5] < '''
        Newer line 2
        Newer line 3
    '''
    code[1:3, 4] < '''
        Newest line 2
    '''