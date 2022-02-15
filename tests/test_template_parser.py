import pytest
from django.template import loader


def test_template_parser_bad_blocks():
    with pytest.raises(Exception) as e:
        loader.render_to_string('test_template_parser_bad_blocks.html')

    assert str(e.value) == """Invalid blocks specified:

    doesnotexist

Valid blocks:

    content"""


def test_template_parser_throwing_away_html():
    with pytest.raises(Exception) as e:
        loader.render_to_string('test_template_parser_throws_away_html.html')

    print(str(e.value))
    assert str(e.value) == """The following html was thrown away when rendering test_template_parser_throws_away_html.html:

    'This gets thrown away silently by django'"""


def test_template_parser_valid_cases():
    loader.render_to_string('test_template_parser_throwing_bad_blocks_base_base.html')
    loader.render_to_string('test_template_parser_no_errors.html')
