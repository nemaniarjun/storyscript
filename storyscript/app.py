# -*- coding: utf-8 -*-
import json
import os

from .compiler import Compiler
from .parser import Grammar, Parser


class App:

    @staticmethod
    def read_story(storypath):
        """
        Reads a story
        """
        with open(storypath, 'r') as file:
            return file.read()

    @staticmethod
    def get_stories(storypath):
        """
        Gets stories from a path
        """
        stories = []
        if os.path.isdir(storypath):
            for root, subdirs, files in os.walk(storypath):
                for file in files:
                    if file.endswith('.story'):
                        stories.append(os.path.join(root, file))
            return stories
        return [storypath]

    @classmethod
    def parse(cls, stories):
        """
        Parses a list of stories, returning their tree.
        """
        results = {}
        for story in stories:
            tree = Parser().parse(cls.read_story(story))
            results[story] = Compiler.compile(tree)
        return results

    @staticmethod
    def services(stories):
        """
        Builds a global list of services from each story's services
        """
        services = []
        for storypath, story in stories.items():
            services += story['services']
        return services

    @classmethod
    def compile(cls, path):
        """
        Parse and compile stories in path to JSON
        """
        stories = cls.get_stories(path)
        compiled_stories = cls.parse(stories)
        services = cls.services(compiled_stories)
        dictionary = {'stories': compiled_stories, 'services': services}
        return json.dumps(dictionary, indent=2)

    @classmethod
    def lex(cls, path):
        """
        Parse and lex stories, producing the list of used tokens
        """
        parser = Parser()
        stories = cls.get_stories(path)
        results = {}
        for story in stories:
            results[story] = parser.lex(cls.read_story(story))
        return results

    @staticmethod
    def grammar():
        return Grammar().build()
