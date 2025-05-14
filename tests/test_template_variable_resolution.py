from django.template import Context, Template
from django.test import TestCase
from django_fastdev.apps import FastDevVariableDoesNotExist
from unittest.mock import patch


class TestFastDevVariableResolution(TestCase):
    def setUp(self):
        self.context = Context({"existing_var": "test_value"})

    def test_nonexistent_variable_with_default_filter(self):
        template = Template('{{ nonexistent_var|default:"fallback" }}')
        result = template.render(self.context)
        self.assertEqual(
            result, "fallback", "Expected fallback value for None with default filter"
        )

    def test_nonexistent_variable_with_default_if_none_filter(self):
        template = Template('{{ nonexistent_var|default_if_none:"fallback" }}')
        result = template.render(self.context)
        self.assertEqual(
            result,
            "fallback",
            "Expected fallback value for None with default_if_none filter",
        )

    def test_nonexistent_variable_without_filters(self):
        template = Template("{{ nonexistent_var }}")
        with self.assertRaises(FastDevVariableDoesNotExist) as cm:
            template.render(self.context)
        self.assertIn("nonexistent_var does not exist in context", str(cm.exception))

    def test_existing_variable_with_default_filter(self):
        template = Template('{{ existing_var|default:"fallback" }}')
        result = template.render(self.context)
        self.assertEqual(
            result, "test_value", "Expected existing variable value with default filter"
        )

    def test_existing_variable_with_default_if_none_filter(self):
        """Test that an existing variable with |default_if_none filter returns its value."""
        template = Template('{{ existing_var|default_if_none:"fallback" }}')
        result = template.render(self.context)
        self.assertEqual(
            result,
            "test_value",
            "Expected existing variable value with default_if_none filter",
        )

    def test_nested_nonexistent_variable_with_default_filter(self):
        template = Template('{{ obj.nonexistent_field|default:"fallback" }}')
        context = Context({"obj": {"existing_field": "value"}})
        result = template.render(context)
        self.assertEqual(
            result,
            "fallback",
            "Expected fallback value for None with nested default filter",
        )

    @patch('django_fastdev.apps.template_is_ignored', lambda *args, **kwargs: True)
    def test_ignored_template_behavior(self):
        from django_fastdev.apps import template_is_ignored
        self.assertTrue(template_is_ignored(), 'Mock patch of template_is_ignored failed')
        template = Template('{{ nonexistent_var|default:"fallback" }}')
        result = template.render(self.context)
        self.assertEqual(
            result, "fallback", "Expected Django default behavior for ignored template"
        )

    def test_nonexistent_variable_with_multiple_filters(self):
        template = Template('{{ nonexistent_var|upper|default:"fallback" }}')
        result = template.render(self.context)
        self.assertEqual(
            result,
            "fallback",
            "Expected fallback value for None with multiple filters including default",
        )
