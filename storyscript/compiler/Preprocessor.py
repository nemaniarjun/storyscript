# -*- coding: utf-8 -*-
from .Faketree import FakeTree


class Preprocessor:
    """
    Performs additional transformations that can't be performed, or would be
    too complicated for the Transformer, before the tree is compiled.
    """

    @staticmethod
    def fake_tree(block):
        """
        Get a fake tree
        """
        return FakeTree(block)

    @staticmethod
    def replace_expression(fake_tree, parent, inline_expression):
        """
        Replaces an inline expression with a fake assignment
        """
        assignment = fake_tree.add_assignment(inline_expression.service)
        entity = parent.entity
        if parent.expression:
            entity = parent.expression.multiplication.exponential.factor.entity
        entity.path.replace(0, assignment.path.child(0))

    @classmethod
    def replace_in_entity(cls, block, statement, entity):
        """
        Replaces an inline expression inside an entity branch.
        """
        fake_tree = cls.fake_tree(block)
        line = statement.line()
        service = entity.path.inline_expression.service
        assignment = fake_tree.add_assignment(service)
        entity.replace(0, assignment.path)
        entity.path.children[0].line = line

    @classmethod
    def service_arguments(cls, block, service):
        """
        Processes the arguments of a service, replacing inline expressions
        """
        fake_tree = cls.fake_tree(block)
        for argument in service.find_data('arguments'):
            expression = argument.node('entity.path.inline_expression')
            if expression:
                cls.replace_expression(fake_tree, argument, expression)

    @classmethod
    def assignment_expression(cls, block, tree):
        """
        Processess an assignment to an expression, replacing it
        """
        fake_tree = cls.fake_tree(block)
        parent = block.rules.assignment.assignment_fragment
        cls.replace_expression(fake_tree, parent, tree.inline_expression)

    @classmethod
    def assignments(cls, block):
        """
        Process assignments, looking for inline expressions, for example:
        a = alpine echo text:(random value) or a = (alpine echo message:'text')
        """
        for assignment in block.find_data('assignment'):
            fragment = assignment.assignment_fragment
            if fragment.service:
                cls.service_arguments(block, fragment.service)
            elif fragment.expression:
                factor = fragment.expression.multiplication.exponential.factor
                if factor.entity.path:
                    if factor.entity.path.inline_expression:
                        cls.assignment_expression(block, factor.entity.path)

    @classmethod
    def service(cls, tree):
        """
        Processes services, looking for inline expressions, for example:
        alpine echo text:(random value)
        """
        service = tree.node('service_block.service')
        if service:
            cls.service_arguments(tree, service)

    @classmethod
    def flow_statement(cls, name, block):
        """
        Processes if statements, looking inline expressions.
        """
        for statement in block.find_data(name):
            if statement.node('entity.path.inline_expression'):
                cls.replace_in_entity(block, statement, statement.entity)

            if statement.child(2):
                if statement.child(2).node('entitypath.inline_expression'):
                    cls.replace_in_entity(block, statement, statement.child(2))

    @classmethod
    def process(cls, tree):
        for block in tree.find_data('block'):
            cls.assignments(block)
            cls.service(block)
            cls.flow_statement('if_statement', block)
            cls.flow_statement('elseif_statement', block)
        return tree
