import pytest
from django.template import Context, Template
from django.template.loader import get_template
from django.test import TestCase
from django_fastdev.apps import FastDevVariableDoesNotExist
from unittest.mock import patch


context = Context({"existing_var": "test_value"})


def test_nonexistent_variable_with_default_filter():
    template = Template('{{ nonexistent_var|default:"fallback" }}')
    result = template.render(context)
    assert result == "fallback", "Expected fallback value for None with default filter"


def test_nonexistent_variable_with_default_if_none_filter():
    template = Template('{{ nonexistent_var|default_if_none:"fallback" }}')
    with pytest.raises(FastDevVariableDoesNotExist) as cm:
        result = template.render(context)
    assert "nonexistent_var does not exist in context" in str(cm.value)


def test_nonexistent_variable_without_filters():
    template = Template("{{ nonexistent_var }}")
    with pytest.raises(FastDevVariableDoesNotExist) as cm:
        template.render(context)
    assert "nonexistent_var does not exist in context" in str(cm.value)


def test_existing_variable_with_default_filter():
    template = Template('{{ existing_var|default:"fallback" }}')
    result = template.render(context)
    assert result == "test_value", "Expected existing variable value with default filter"


def test_existing_variable_with_default_if_none_filter():
    """Test that an existing variable with |default_if_none filter returns its value."""
    template = Template('{{ existing_var|default_if_none:"fallback" }}')
    result = template.render(context)
    assert result == "test_value", "Expected existing variable value with default_if_none filter"


def test_nested_nonexistent_variable_with_default_filter():
    template = Template('{{ obj.nonexistent_field|default:"fallback" }}')
    context = Context({"obj": {"existing_field": "value"}})
    result = template.render(context)
    assert result == "fallback", "Expected fallback value for None with nested default filter"


def test_ignored_template_with_filter():
    template = get_template('ignored/test_ignored_template_with_filter.html')
    result = template.render().strip()
    assert result == "fallback", "Expected Django default behavior for ignored template"


def test_nonexistent_variable_with_multiple_filters():
    template = Template('{{ nonexistent_var|upper|default:"fallback" }}')
    result = template.render(context)
    assert result == "fallback", "Expected fallback value for None with multiple filters including default"


def test_nonexistent_variable_with_multiple_filters2():
    template = Template('{{ nonexistent_var|default:"fallback"|upper }}')
    result = template.render(context)
    assert result == "FALLBACK", "Expected fallback value for None with multiple filters including default"
