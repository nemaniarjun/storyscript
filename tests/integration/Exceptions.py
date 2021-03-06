# -*- coding: utf-8 -*-
import re

from pytest import raises

from storyscript.Story import Story
from storyscript.exceptions.StoryError import StoryError

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


def test_exception_service_name(capsys):
    with raises(StoryError) as e:
        Story('al.pine echo').process()

    message = e.value.message()
    # test with coloring once, but we representing ANSI color codes is tricky
    lines = ansi_escape.sub('', message).splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    al.pine echo'
    assert lines[5] == "E0002: A service name can't contain `.`"


def test_exception_arguments_noservice(capsys):
    with raises(StoryError) as e:
        Story('length:10').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    length:10'
    assert lines[5] == 'E0003: You have defined an argument, but not a service'


def test_exception_variables_backslash(capsys):
    with raises(StoryError) as e:
        Story('a/b = 0').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    a/b = 0'
    assert lines[5] == "E0005: A variable name can't contain `/`"


def test_exception_variables_dash(capsys):
    with raises(StoryError) as e:
        Story('a-b = 0').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    a-b = 0'
    assert lines[5] == "E0006: A variable name can't contain `-`"


def test_exception_return_outside(capsys):
    with raises(StoryError) as e:
        Story('return 0').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 8'
    assert lines[2] == '1|    return 0'
    assert lines[5] == 'E0004: `return` is allowed only inside functions'


def test_exception_missing_value(capsys):
    with raises(StoryError) as e:
        Story('a = ').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 5'
    assert lines[2] == '1|    a = '
    assert lines[5] == 'E0007: Missing value after `=`'


def test_exception_file_not_found(capsys):
    with raises(StoryError) as e:
        Story.from_file('this-file-does-not-exist')
    message = e.value.message()
    assert 'File "this-file-does-not-exist" not found at' in message
