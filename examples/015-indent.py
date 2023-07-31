from canim import code_animation, CodeScene, themes


@code_animation
def example(scene: CodeScene):
    code = scene.code(language='python', prompts=['>>> ', '... '], theme=themes.Bauhaus(animate=False))
    code >> '''
    >>> x = 1
    >>> x = 2
    >>> x = 3
    '''
    code.lines[0].append_lines('>>> if True:', indent_lines=1, indent_prompt='... ')
    code.lines[1].remove(dedent_lines=1, dedent_prompt='>>> ')
    scene.wait(5)