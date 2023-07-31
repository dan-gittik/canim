from canim import code_animation, CodeScene, themes

from manim import UP, DOWN


@code_animation
def example(scene: CodeScene):
    theme = themes.Window(background_color='#cccccc', animate=True)
    code = scene.code(small=True, theme=theme)
    lines = code >> '''
        Line 1
        Line 2
        Line 3
        Line 4
        Line 5
    '''
    lines += code >> '''
        Line 6
        Line 7
        Line 8
        Line 9
        Line 10
    '''
    # Hacky test before scroll into view is automatic.
    scene.play(*[line.text.animate.shift(UP * 2) for line in lines])
    scene.play(*[line.text.animate.shift(DOWN * 4) for line in lines])