import inspect
import os
import re
import subprocess
import sys
import threading
from functools import cache
from typing import Optional
import warnings
from contextlib import (
    contextmanager,
    nullcontext,
)
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings
from django.db.models import (
    Model,
    QuerySet,
)
from django.forms import Form
from django.template import Context
from django.template.base import (
    FilterExpression,
    TextNode,
    Variable,
    VariableDoesNotExist,
    TokenType,
)
from django.template.defaulttags import (
    FirstOfNode,
    IfNode,
)
from django.template.loader_tags import (
    BlockNode,
    ExtendsNode,
)
from django.templatetags.i18n import BlockTranslateNode
from django.urls.exceptions import NoReverseMatch
from django.views.debug import DEBUG_ENGINE


class FastDevVariableDoesNotExist(Exception):
    pass


_local = threading.local()
_local.ignore_errors = False
_local.deprecation_warning = None


@contextmanager
def ignore_template_errors(deprecation_warning=None):
    _local.ignore_errors = True
    _local.deprecation_warning = deprecation_warning
    try:
        yield
    finally:
        _local.ignore_errors = False
        _local.deprecation_warning = None


def get_path_for_django_project() -> Path:
    try:
        path = settings.BASE_DIR
    except AttributeError:
        path = settings.ROOT_DIR
    return Path(path).resolve(strict=True)


def get_gitignore_path():
    path = get_path_for_django_project()
    if os.path.isfile(os.path.join(path, ".gitignore")):
        return os.path.join(path, ".gitignore")
    else:
        return None
    

def is_absolute_url(url):
    return bool(url.startswith('/') or url.startswith('http://') or url.startswith('https://'))
    

def validate_static_url_setting():
    """
    Validates the STATIC_URL setting to ensure it is indeed absolute url.

    This function checks whether the `STATIC_URL` setting, typically defined in the 
    application's settings, is set correctly. It ensures that the URL starts with either a '/' 
    or 'http'. If the`STATIC_URL` does not start with either, an exception is raised.

    Raises:
        Exception: If the `STATIC_URL` does not start with '/' or 'http'.

    Returns:
        None
    """
    static_url = getattr(settings, 'STATIC_URL', None)
    
    # check for static url
    if static_url and not is_absolute_url(static_url):
        print(f"""
        WARNING:
        You have STATIC_URL set to {static_url} in your settings.py file.

        It should start with either a '/' or 'http' to ensure it is an absolute URL.

        """, file=sys.stderr)

    return


def check_for_migrations_in_gitignore(line):
    return bool(re.search(r"\bmigrations\b", line))


def is_venv_ignored(project_path: Path) -> Optional[bool]:
    try:
        # if sys.prefix isn't inside of get_path_for_django_project(), then consider it ignored
        Path(sys.prefix).relative_to(project_path)
    except ValueError:
        return True

    try:
        # ensure git is invoked as though it were run from the project directory, since
        # manage.py can be invoked from other directories.
        check_ignore = subprocess.run(["git", "-C", project_path, "check-ignore", "--quiet", sys.prefix])
        return check_ignore.returncode == 0
    except FileNotFoundError:
        print("git is not installed. django-fastdev can't check if venv is ignored in .gitignore", file=sys.stderr)
        return None


def check_for_pycache_in_gitignore(line):
    return bool(re.search(r"__pycache__\b", line))


def validate_gitignore(path):
    project_path = get_path_for_django_project()
    bad_line_numbers_for_ignoring_migration = []
    list_of_subfolders = [f.name for f in os.scandir(project_path) if f.is_dir()]
    is_pycache_ignored = False

    with open(path, "r") as git_ignore_file:
        for (index, line) in enumerate(git_ignore_file.readlines()):

            if check_for_migrations_in_gitignore(line):
                bad_line_numbers_for_ignoring_migration.append(index+1)

            if check_for_pycache_in_gitignore(line):
                is_pycache_ignored = True

        if bad_line_numbers_for_ignoring_migration:
            print(f"""
            You have excluded migrations folders from git

            This is not a good idea! It's very important to commit all your migrations files into git for migrations to work properly.

            https://docs.djangoproject.com/en/dev/topics/migrations/#version-control for more information

            Bad pattern on lines : {', '.join(map(str, bad_line_numbers_for_ignoring_migration))}""", file=sys.stderr)

        if is_venv_ignored(project_path) is False:
            print(f"""
            {sys.prefix} is not ignored in .gitignore.
            Please add {sys.prefix} to .gitignore.
            """, file=sys.stderr)

        if not is_pycache_ignored and "__pycache__" in list_of_subfolders:
            print(f"""
            __pycache__ is not ignored in .gitignore.
            Please add __pycache__ to .gitignore.
            """, file=sys.stderr)


def validate_fk_field(model):
    found_problems = []
    # noinspection PyProtectedMember
    for field in model._meta.fields:
        if field.get_internal_type() == "ForeignKey":
            if field.name.endswith(("Id", "_Id", "ID", "_ID", "_id", "iD")):
                found_problems.append(field.name)
    return found_problems


def get_models_with_badly_named_pk():
    import django.apps

    new_line = "\n"
    output = ""

    for model in django.apps.apps.get_models():
        found_problems = validate_fk_field(model)
        if found_problems:
            output += f"""{' '*8}{model.__name__}{new_line}{''.join([f"{' '*12}- {i}{new_line}" for i in found_problems])}"""
    if output:
        print(
            f"""
        You have the following models with ForeignKey that end with 'id' in the name:

{output}

        This is wrong. The Django ForeignKey is a relation to a model object, not it's ID, so this is correct:
            car = ForeignKey(Car)

        Django will create a `car_id` field under the hood that is the ID of that field (normally a number).""",
            file=sys.stderr
        )


def strict_if():
    return getattr(settings, 'FASTDEV_STRICT_IF', False)


def strict_template_checking():
    return getattr(settings, 'FASTDEV_STRICT_TEMPLATE_CHECKING', False)


def get_venv_folder_name():
    import os

    path_to_venv = os.environ["VIRTUAL_ENV"]
    venv_folder = os.path.basename(path_to_venv)
    return venv_folder


@cache
def get_ignored_template_list():
    ignored_templates_settings = getattr(settings, 'FASTDEV_IGNORED_TEMPLATES', [])
    ignored_templates = list()
    if ignored_templates_settings:
        for entry in ignored_templates_settings:
            ignored_templates.append(re.compile(entry))
    return ignored_templates


@cache
def template_is_ignored(origin_name):
    for expr in get_ignored_template_list():
        if expr.match(origin_name):
            return True
    return False


class FastDevConfig(AppConfig):
    name = 'django_fastdev'
    verbose_name = 'django-fastdev'
    default = True

    def ready(self):
        orig_resolve = FilterExpression.resolve

        def resolve_override(self, context, ignore_failures=False, ignore_failures_for_real=False):
            if context.template_name is None and '{% if exception_type %}{{ exception_type }}' in context.template.source:
                # best guess we are in the 500 error page, do the default
                return orig_resolve(self, context)

            # If a template has been explicitly ignored by the developer, do the default
            if template_is_ignored(context.template.origin.name):
                return orig_resolve(self, context)

            if isinstance(self.var, Variable):
                try:
                    self.var.resolve(context)
                except FastDevVariableDoesNotExist:
                    raise
                except VariableDoesNotExist as e:
                    if not strict_template_checking():
                        # worry only about templates inside our project dir; if they
                        # exist elsewhere, then go to standard django behavior
                        venv_dir = os.environ.get('VIRTUAL_ENV', '')
                        origin = context.template.origin.name
                        if (
                            origin != '<unknown source>' and
                            'django-fastdev/tests/' not in origin
                            and (
                                not origin.startswith(str(settings.BASE_DIR))
                                or (venv_dir and origin.startswith(venv_dir))
                            )
                        ):
                            return orig_resolve(self, context, ignore_failures=ignore_failures)
                    if ignore_failures_for_real or getattr(_local, 'ignore_errors', False):
                        if _local.deprecation_warning:
                            warnings.warn(_local.deprecation_warning, category=DeprecationWarning)
                        return orig_resolve(self, context, ignore_failures=True)

                    if context.template.engine == DEBUG_ENGINE:
                        return orig_resolve(self, context, ignore_failures=ignore_failures)

                    bit, current = e.params
                    if len(self.var.lookups) == 1:
                        available = '\n    '.join(sorted(context.flatten().keys()))
                        raise FastDevVariableDoesNotExist(f'''{self.var} does not exist in context. Available top level variables:

    {available}
''')
                    else:
                        full_name = '.'.join(self.var.lookups)
                        extra = ''

                        if isinstance(current, Context):
                            current = current.flatten()

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

        # {% if %}
        def if_render_override(self, context):
            for condition, nodelist in self.conditions_nodelists:
                if condition is not None:  # if / elif clause
                    context_handler = nullcontext()
                    if not strict_if() or '{% if exception_type %}{{ exception_type }}' in context.template.source:
                        context_handler = ignore_template_errors(deprecation_warning='set FASTDEV_STRICT_IF in settings, and use {% ifexists %} instead of {% if %} to check if a variable exists.')

                    with context_handler:
                        try:
                            match = condition.eval(context)
                        except VariableDoesNotExist:
                            match = None
                else:  # else clause
                    match = True

                if match:
                    return nodelist.render(context)

            return ''

        IfNode.render = if_render_override

        # Better reverse() errors
        import django.urls.resolvers as res
        res.NoReverseMatch = FastDevNoReverseMatch
        import django.urls.base as bas
        bas.NoReverseMatch = FastDevNoReverseMatchNamespace

        # Forms validation
        orig_form_full_clean = Form.full_clean

        def fastdev_full_clean(self):
            orig_form_full_clean(self)
            from django.conf import settings
            if settings.DEBUG:
                prefix = 'clean_'
                for name in dir(self):
                    if name.startswith(prefix) and callable(getattr(self, name)) and name[len(prefix):] not in self.fields:
                        fields = '\n    '.join(sorted(self.fields.keys()))

                        raise InvalidCleanMethod(f"""Clean method {name} of class {self.__class__.__name__} won't apply to any field. Available fields:

    {fields}""")

        Form.full_clean = fastdev_full_clean

        # QuerySet error messages
        orig_queryset_get = QuerySet.get

        def fixup_query_exception(e, args, kwargs):
            assert len(e.args) == 1
            message = e.args[0]
            if args:
                message += f'\n\nQuery args:\n\n    {args}'
            if kwargs:
                kwargs = '\n    '.join([f'{k}: {v!r}' for k, v in kwargs.items()])
                message += f'\n\nQuery kwargs:\n\n    {kwargs}'
            e.args = (message,)

        def fast_dev_get(self, *args, **kwargs):
            try:
                return orig_queryset_get(self, *args, **kwargs)
            except self.model.DoesNotExist as e:
                fixup_query_exception(e, args, kwargs)
                raise
            except self.model.MultipleObjectsReturned as e:
                fixup_query_exception(e, args, kwargs)
                raise

        QuerySet.get = fast_dev_get

        if settings.DEBUG:
            # Gitignore validation
            git_ignore = get_gitignore_path()
            if git_ignore:
                threading.Thread(target=validate_gitignore, args=(git_ignore, )).start()

            # ForeignKey validation
            threading.Thread(target=get_models_with_badly_named_pk).start()

        # Fix blocktrans
        orig_blocktrans_render_token_list = BlockTranslateNode.render_token_list

        validate_static_url_setting()

        def fastdev_render_token_list(self, tokens):
            for token in tokens:
                if token.token_type == TokenType.VAR:
                    if '.' in token.contents:
                        raise FastDevVariableDoesNotExist("You can't use dotted paths in blocktrans. You must use {% with foo = something.bar %} around the blocktrans.")
            return orig_blocktrans_render_token_list(self, tokens)

        BlockTranslateNode.render_token_list = fastdev_render_token_list

        # Extends validation
        def collect_nested_blocks(node):
            if isinstance(node, BlockNode):
                result = {node.name}
            else:
                result = set()
            if hasattr(node, 'nodelist'):
                for x in node.nodelist:
                    result |= collect_nested_blocks(x)
            return result

        def get_extends_node_parent(extends_node, context):
            compiled_parent = extends_node.get_parent(context)
            del context.render_context[extends_node.context_key]  # remove our history of doing this
            return compiled_parent

        def collect_valid_blocks(template, context):
            result = set()
            for x in template.nodelist:
                if isinstance(x, BlockNode):
                    result |= collect_nested_blocks(x)
                elif isinstance(x, ExtendsNode):
                    result |= collect_nested_blocks(x)
                    result |= collect_valid_blocks(get_extends_node_parent(x, context), context)
            return result

        orig_extends_render = ExtendsNode.render

        def extends_render(self, context):
            if settings.DEBUG:
                valid_blocks = collect_valid_blocks(get_extends_node_parent(self, context), context)
                actual_blocks = {x.name for x in self.nodelist if isinstance(x, BlockNode)}
                invalid_blocks = actual_blocks - valid_blocks
                if invalid_blocks:
                    invalid_names = '    ' + '\n    '.join(sorted(invalid_blocks))
                    valid_names = '    ' + '\n    '.join(sorted(valid_blocks))
                    raise Exception(f'Invalid blocks specified:\n\n{invalid_names}\n\nValid blocks:\n\n{valid_names}')

                # Validate no thrown away (non-whitespace) text blocks
                thrown_away_text = '\n    '.join([repr(x.s.strip()) for x in self.nodelist if isinstance(x, TextNode) and x.s.strip()])
                assert not thrown_away_text, f'The following html was thrown away when rendering {self.origin.template_name}:\n\n    {thrown_away_text}'

            return orig_extends_render(self, context)

        ExtendsNode.render = extends_render

        def fastdev_model__repr__(self):
            return "<%s pk=%s>" % (self.__class__.__name__, self.pk)

        Model.__repr__ = fastdev_model__repr__


class InvalidCleanMethod(Exception):
    pass


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
