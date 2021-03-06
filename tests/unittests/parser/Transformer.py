# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer
from lark.lexer import Token

from pytest import fixture, mark, raises

from storyscript.exceptions import StorySyntaxError
from storyscript.parser import Transformer, Tree


@fixture
def syntax_error(patch):
    patch.init(StorySyntaxError)
    return StorySyntaxError.__init__


def test_transformer():
    keywords = ['function', 'if', 'else', 'foreach', 'return', 'returns',
                'try', 'catch', 'finally', 'when', 'as', 'import', 'while',
                'raise']
    future_keywords = ['async', 'story', 'assert', 'called', 'mock']
    assert Transformer.reserved_keywords == keywords
    assert Transformer.future_reserved_keywords == future_keywords
    assert issubclass(Transformer, LarkTransformer)


@mark.parametrize('keyword', [
    'function', 'if', 'else', 'foreach', 'return', 'returns', 'try', 'catch',
    'finally', 'when', 'as', 'import', 'while', 'raise'
])
def test_transformer_is_keyword(syntax_error, keyword):
    token = Token('any', keyword)
    with raises(StorySyntaxError):
        Transformer.is_keyword(token)
    name = 'reserved_keyword_{}'.format(keyword)
    syntax_error.assert_called_with(name, token=token)


@mark.parametrize('keyword', [
    'async', 'story', 'mock', 'assert', 'called', 'mock'
])
def test_transformer_is_keyword_future(syntax_error, keyword):
    token = Token('any', keyword)
    with raises(StorySyntaxError):
        Transformer.is_keyword(token)
    name = 'future_reserved_keyword_{}'.format(keyword)
    syntax_error.assert_called_with(name, token=token)


def test_transformer_implicit_output(tree):
    """
    Ensures Transformer.implicit_output adds an output tree when needed
    """
    tree.service_fragment.output = None
    tree.service_fragment.children = []
    Transformer.implicit_output(tree)
    expected = Tree('output', [tree.service_fragment.command.child()])
    assert tree.service_fragment.children[-1] == expected


def test_transformer_implicit_output_none(tree):
    assert Transformer.implicit_output(tree) is None


def test_transformer_arguments():
    assert Transformer.arguments('matches') == Tree('arguments', 'matches')


def test_transformer_arguments_short():
    matches = [Tree('path', ['token'])]
    expected = ['token', Tree('path', ['token'])]
    assert Transformer.arguments(matches) == Tree('arguments', expected)


def test_transformer_assignment(magic):
    matches = [magic()]
    assert Transformer.assignment(matches) == Tree('assignment', matches)


def test_transformer_assignment_error_backslash(syntax_error, magic):
    token = magic(value='/')
    matches = [magic(children=[token])]
    with raises(StorySyntaxError):
        Transformer.assignment(matches)
    syntax_error.assert_called_with('variables_backslash', token=token)


def test_transformer_assignment_error_dash(syntax_error, magic):
    token = magic(value='-')
    matches = [magic(children=[token])]
    with raises(StorySyntaxError):
        Transformer.assignment(matches)
    syntax_error.assert_called_with('variables_dash', token=token)


def test_transformer_command(patch, magic):
    patch.object(Transformer, 'is_keyword')
    result = Transformer.command(['matches'])
    Transformer.is_keyword.assert_called_with('matches')
    assert result == Tree('command', ['matches'])


def test_transformer_path(patch):
    patch.object(Transformer, 'is_keyword')
    result = Transformer.path(['matches'])
    Transformer.is_keyword.assert_called_with('matches')
    assert result == Tree('path', ['matches'])


def test_transformer_service_block():
    """
    Ensures service_block nodes are transformed correctly
    """
    assert Transformer.service_block([]) == Tree('service_block', [])


def test_transformer_service_block_when(patch, tree):
    """
    Ensures service_block nodes with a when block are transformed correctly
    """
    patch.object(Transformer, 'implicit_output')
    tree.block.rules = None
    matches = ['service_block', tree]
    result = Transformer.service_block(matches)
    Transformer.implicit_output.assert_called_with('service_block')
    assert result == Tree('service_block', matches)


def test_transformer_service_block_indented_args(tree, magic):
    """
    Ensures service_block with indented arguments are transformed correctly.
    """
    tree.find_data.return_value = ['argument']
    block = magic()
    matches = [block, tree]
    result = Transformer.service_block(matches)
    block.service_fragment.children.append.assert_called_with('argument')
    assert result == Tree('service_block', [block])


def test_transformer_when_block(patch, tree):
    """
    Ensures when_block nodes are transformed correctly
    """
    patch.object(Transformer, 'implicit_output')
    result = Transformer.when_block([tree])
    Transformer.implicit_output.assert_called_with(tree)
    assert result == Tree('when_block', [tree])


@mark.parametrize('rule', ['start', 'line', 'block', 'statement'])
def test_transformer_rules(rule):
    result = getattr(Transformer(), rule)(['matches'])
    assert isinstance(result, Tree)
    assert result.data == rule
    assert result.children == ['matches']
