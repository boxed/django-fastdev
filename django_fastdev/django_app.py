import threading
import inspect
from contextlib import contextmanager

from django.apps import AppConfig
from django.template.base import (
    FilterExpression,
    TextNode,
    Variable,
    VariableDoesNotExist,
)
from django.template.defaulttags import (
    FirstOfNode,
    IfNode,
)
from django.template.loader_tags import (
    BlockNode,
    ExtendsNode,
)
from django.urls.exceptions import NoReverseMatch


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

        # Better reverse() errors
        import django.urls.resolvers as res
        res.NoReverseMatch = FastDevNoReverseMatch
        import django.urls.base as bas
        bas.NoReverseMatch = FastDevNoReverseMatchNamespace

        # Extends validation
        orig_extends_render = ExtendsNode.render

        def collect_valid_blocks(extends_node, context):
            compiled_parent = extends_node.get_parent(context)
            del context.render_context[extends_node.context_key]  # remove our history of doing this
            extends_nodes = {x for x in compiled_parent.nodelist if isinstance(x, ExtendsNode)}
            if extends_nodes:
                assert len(extends_nodes) == 1
                return collect_valid_blocks(extends_nodes.pop(), context)

            return {x.name for x in compiled_parent.nodelist if isinstance(x, BlockNode)}

        def extends_render(self, context):
            valid_blocks = collect_valid_blocks(self, context)
            actual_blocks = {x.name for x in self.nodelist if isinstance(x, BlockNode)}
            invalid_blocks = actual_blocks - valid_blocks
            if invalid_blocks:
                invalid_names = '    ' + '\n    '.join(sorted(invalid_blocks))
                valid_names = '    ' + '\n    '.join(sorted(valid_blocks))
                raise Exception(f'Invalid blocks specified:\n\n{invalid_names}\n\nValid blocks:\n\n{valid_names}')

            # TODO: validate no thrown away (non-whitespace) text blocks! And write a test for that!
            thrown_away_text = '\n    '.join([repr(x.s.strip()) for x in self.nodelist if isinstance(x, TextNode) and x.s.strip()])
            assert not thrown_away_text, f'The following html was thrown away when rendering {self.origin.template_name}:\n\n    {thrown_away_text}'

            return orig_extends_render(self, context)

        ExtendsNode.render = extends_render


class FastDevNoReverseMatchNamespace(NoReverseMatch):

    def __init__(self, msg):
        from django.conf import settings
        if settings.DEBUG:
            frame = inspect.currentframe().f_back
            resolver = frame.f_locals['resolver']

            msg += '\n\nAvailable namespaces:\n    '
            msg += '\n    '.join(sorted(resolver.namespace_dict.keys()))

        super().__init__(msg)


class FastDevNoReverseMatch(NoReverseMatch):

    def __init__(self, msg):
        from django.conf import settings
        if settings.DEBUG:
            frame = inspect.currentframe().f_back

            msg += '\n\nThese names exist:\n\n    '
            
            names = []

            resolver = frame.f_locals['self']
            for k in resolver.reverse_dict.keys():
                if callable(k):
                    continue
                names.append(k)

            msg += '\n    '.join(sorted(names))

        super().__init__(msg)
