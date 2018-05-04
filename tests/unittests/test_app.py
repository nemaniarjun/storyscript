import json
import os

from pytest import fixture

from storyscript.app import App
from storyscript.parser import Parser


@fixture
def storypath():
    return 'test.story'


@fixture
def story_teardown(request, storypath):
    def teardown():
        os.remove(storypath)
    request.addfinalizer(teardown)


@fixture
def story(story_teardown, storypath):
    story = 'run\n\tpass'
    with open(storypath, 'w') as file:
        file.write(story)
    return story


@fixture
def read_story(mocker):
    mocker.patch.object(App, 'read_story')


@fixture
def parser(mocker):
    mocker.patch.object(Parser, '__init__', return_value=None)
    mocker.patch.object(Parser, 'parse')


def test_app_read_story(story, storypath):
    """
    Ensures App.read_story reads a story
    """
    result = App.read_story(storypath)
    assert result == story


def test_app_get_stories(mocker):
    """
    Ensures App.get_stories returns the original path if it's not a directory
    """
    mocker.patch.object(os.path, 'isdir', return_value=False)
    assert App.get_stories('stories') == ['stories']


def test_app_get_stories_directory(mocker):
    """
    Ensures App.get_stories returns stories in a directory
    """
    mocker.patch.object(os.path, 'isdir')
    mocker.patch.object(os, 'walk',
                        return_value=[('root', [], ['one.story', 'two'])])
    assert App.get_stories('stories') == ['root/one.story']


def test_app_parse(patch, parser, read_story):
    """
    Ensures App.parse runs Parser.parse
    """
    patch.init(Parser)
    patch.object(Parser, 'parse')
    patch.object(App, 'get_stories', return_value=['one.story'])
    result = App.parse('path')
    App.get_stories.assert_called_with('path')
    App.read_story.assert_called_with('one.story')
    Parser().parse.assert_called_with(App.read_story(), json=False)
    assert result == {'one.story': Parser().parse()}


def test_app_parse_json(patch, parser, read_story):
    """
    Ensures App.parse runs Parser.parse with json
    """
    patch.init(Parser)
    patch.object(Parser, 'parse')
    patch.object(App, 'get_stories', return_value=['one.story'])
    App.parse('path', json=True)
    Parser().parse.assert_called_with(App.read_story(), json=True)


def test_app_lexer(patch, read_story):
    patch.init(Parser)
    patch.object(Parser, 'lex')
    patch.object(App, 'get_stories', return_value=['one.story'])
    result = App.lex('/path')
    App.read_story.assert_called_with('one.story')
    Parser.lex.assert_called_with(App.read_story())
    assert result == {'one.story': Parser.lex()}
