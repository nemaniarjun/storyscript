# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from ..parser import Tree


class FakeTree:
    """
    Creates fake trees that are not in the original story source.
    """

    @staticmethod
    def line(line):
        """
        Creates a fake line number, using a given line as base so that
        line - 1 < fake line < line
        """
        base = int(line) - 1
        extension = str(uuid.uuid4().int)[:8]
        return '{}.{}'.format(base, extension)

    @staticmethod
    def path(line):
        """
        Creates a virtual path tree.
        """
        path = '${}'.format(uuid.uuid4().hex[:8])
        return Tree('path', [Token('NAME', path, line=line)])
