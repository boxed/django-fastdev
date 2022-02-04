import threading
from contextlib import contextmanager

from django.apps import AppConfig
from django.template.base import (
    FilterExpression,
    Variable,
    VariableDoesNotExist,
)
from django.template.defaulttags import (
    FirstOfNode,
    IfNode,
)


class FastDevVariableDoesNotExist(Exception):
    pass


_local = threading.local()


@contextmanager
def ignore_template_errors():
    _local.ignore_errors = True
    try:
        yield
    finally:
        _local.ignore_errors = False


class FastDevConfig(AppConfig):
    name = 'django_fastdev'
    verbose_name = 'django-fastdev'

    def ready(self):
        orig_resolve = FilterExpression.resolve

        def resolve_override(self, context, ignore_failures=False, ignore_failures_for_real=False):
            if ignore_failures_for_real or getattr(_local, 'ignore_errors', False):
                return orig_resolve(self, context, ignore_failures=True)

            if isinstance(self.var, Variable):
                try:

                    self.var.resolve(context)
                except FastDevVariableDoesNotExist:
                    raise
                except VariableDoesNotExist as e:
                    bit, current = e.params
                    if len(self.var.lookups) == 1:
                        available = '\n    '.join(sorted(context.flatten().keys()))
                        raise FastDevVariableDoesNotExist(f'''{self.var} does not exist in context. Available top level variables:

    {available}
''')
                    else:
                        full_name = '.'.join(self.var.lookups)
                        extra = ''

                        if isinstance(current, dict):
                            available_keys = '\n    '.join(sorted(current.keys()))
                            extra = f'\nYou can access keys in the dict by their name. Available keys:\n\n    {available_keys}\n'
                            error = f"dict does not have a key '{bit}', and does not have a member {bit}"
                        else:
                            name = f'{type(current).__module__}.{type(current).__name__}'
                            error = f'{name} does not have a member {bit}'
                        available = '\n    '.join(sorted(x for x in dir(current) if not x.startswith('_')))

                        raise FastDevVariableDoesNotExist(f'''Tried looking up {full_name} in context

{error}
{extra}
Available attributes:

    {available}

The object was: {current!r}
''')

            return orig_resolve(self, context, ignore_failures)

        FilterExpression.resolve = resolve_override

        # {% firstof %}
        first_of_render_orig = FirstOfNode.render

        def first_of_render_override(self, context):
            with ignore_template_errors():
                return first_of_render_orig(self, context)

        FirstOfNode.render = first_of_render_override

        # {% firstof %}
        if_render_orig = IfNode.render

        def if_render_override(self, context):
            with ignore_template_errors():
                return if_render_orig(self, context)

        IfNode.render = if_render_override
