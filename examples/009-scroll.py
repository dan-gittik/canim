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
    code >> '''
        Line 8
        Line 9
        Line 10
    '''
    code << 'Line 0'
    ~code[9]
    code.scroll_to_end(5)
    code >> '''
        Line 11
        Line 12
    '''
    code >> '''
        Line 13
        Line 14
        Line 15
    '''