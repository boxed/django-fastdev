from django import template
# noinspection PyProtectedMember
from django.template import (
    Node,
    NodeList,
    TemplateSyntaxError,
)
from django.template.defaulttags import TemplateIfParser

from django_fastdev.apps import FastDevVariableDoesNotExist

register = template.Library()


class IfExistsNode(Node):

    def __init__(self, conditions_nodelists):
        self.conditions_nodelists = conditions_nodelists

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def __iter__(self):
        for _, nodelist in self.conditions_nodelists:
            yield from nodelist

    @property
    def nodelist(self):
        return NodeList(self)

    def render(self, context):
        for condition, nodelist in self.conditions_nodelists:

            if condition is not None:           # ifexists / elifexists clause
                try:
                    condition.eval(context)
                    match = True
                except FastDevVariableDoesNotExist:
                    match = False
            else:                               # else clause
                match = True

            if match:
                return nodelist.render(context)

        return ''


@register.tag
def ifexists(parser, token):
    # {% ifexists ... %}
    bits = token.split_contents()[1:]
    condition = TemplateIfParser(parser, bits).parse()
    nodelist = parser.parse(('elifexists', 'else', 'endifexists'))
    conditions_nodelists = [(condition, nodelist)]
    token = parser.next_token()

    # {% elifexists ... %} (repeatable)
    while token.contents.startswith('elifexists'):
        bits = token.split_contents()[1:]
        condition = TemplateIfParser(parser, bits).parse()
        nodelist = parser.parse(('elifexists', 'else', 'endifexists'))
        conditions_nodelists.append((condition, nodelist))
        token = parser.next_token()

    # {% else %} (optional)
    if token.contents == 'else':
        nodelist = parser.parse(('endifexists',))
        conditions_nodelists.append((None, nodelist))
        token = parser.next_token()

    # {% endif %}
    if token.contents != 'endifexists':
        raise TemplateSyntaxError('Malformed template tag at line {}: "{}"'.format(token.lineno, token.contents))

    return IfExistsNode(conditions_nodelists)
