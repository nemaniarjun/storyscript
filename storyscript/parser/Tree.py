# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from ..exceptions import CompilerError


class Tree(LarkTree):
    """
    Wraps the original Tree class from lark, providing many useful
    enhancements.
    """

    @staticmethod
    def walk(tree, path):
        for item in tree.children:
            if isinstance(item, Tree):
                if item.data == path:
                    return item

    def node(self, path):
        """
        Finds a subtree or a nested subtree, using path
        """
        shards = path.split('.')
        current = None
        for shard in shards:
            if current is None:
                current = self.walk(self, shard)
            else:
                current = self.walk(current, shard)
        return current

    def child(self, index):
        if len(self.children) > index:
            return self.children[index]

    def find(self, path):
        """
        Wraps LarkTree.find_data, making it easier to use.
        """
        return list(self.find_data(path))

    def _find_position(self, position):
        """
        Finds the request positional attribute of a tree, by finding the
        first token its first token and returning the token's positional
        attribute
        """
        for child in self.children:
            if isinstance(child, Token):
                return str(getattr(child, position))
            return child._find_position(position)

    def line(self):
        """
        Finds the line number of a tree using _find_position
        """
        return self._find_position('line')

    def column(self):
        """
        Finds the column number of a tree using _find_position
        """
        return self._find_position('column')

    def end_column(self):
        """
        Finds the end column number of a tree using _find_position
        """
        return self._find_position('end_column')

    def insert(self, item):
        """
        Inserts an item into the current tree.
        """
        self.children.insert(0, item)

    def rename(self, new_name):
        """
        Renames the current tree
        """
        self.data = new_name

    def replace(self, index, item):
        """
        Replaces a child at the given index
        """
        self.children[index] = item

    def extract_path(self):
        """
        Extracts the path name from a path tree
        """
        string = ''
        for child in self.children:
            if isinstance(child, Tree):
                string = '{}.{}'.format(string, child.child(0).value)
            else:
                string += child.value
        return string

    def is_unary(self):
        """
        Whether the current expression tree is an unary expression.
        """
        if self.data == 'expression':
            if len(self.children) == 1:
                if len(self.child(0).children) == 1:
                    if len(self.child(0).child(0).children) == 1:
                        return True
        return False

    def find_operator(self):
        """
        Finds the operator of a simple expression (two operands). The operator
        can be at different depths, depending on the expression type.
        """
        if isinstance(self.child(1), Token):
            return self.child(1)
        if self.child(0):
            if isinstance(self.multiplication.child(1), Token):
                return self.multiplication.child(1)
            if isinstance(self.multiplication.exponential, Tree):
                if isinstance(self.multiplication.exponential.child(1), Token):
                    return self.multiplication.exponential.child(1)
        return self.multiplication.exponential.factor.child(0)

    def expect(self, cond, error):
        """
        Throws a compiler error with message if the condition is falsy.
        """
        if not cond:
            raise CompilerError(error, tree=self)

    def __getattr__(self, attribute):
        return self.node(attribute)
