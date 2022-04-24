from django_fastdev.apps import FastDevVariableDoesNotExist, check_for_migrations_in_gitignore, check_for_pycache_in_gitignore, check_for_venv_in_gitignore, check_for_vscode_cache_in_gitignore

def test_if_gitignore_has_migrations():
    line = 'migrations/'
    errors = check_for_migrations_in_gitignore(line)
    errors_expected = True
    assert errors == errors_expected


def test_if_gitignore_doesnt_have_migrations():
    line = 'not_migrations/'
    errors = check_for_migrations_in_gitignore(line)
    assert errors == False


def test_if_venv_is_ignored():
    line= 'venv/'
    errors = check_for_venv_in_gitignore('venv',line)
    assert errors == True


def test_if_venv_is_not_ignored():
    line= ''
    errors = check_for_venv_in_gitignore('venv',line)
    assert errors == False


def test_if_pycache_is_ignored_or_not():
    line = '__pycache__'
    errors = check_for_pycache_in_gitignore(line)
    assert errors == True

    line = ''
    errors = check_for_pycache_in_gitignore(line)
    assert errors == False


def test_if_vscode_cache_is_ignored_or_not():
    line = '.vscode'
    errors = check_for_vscode_cache_in_gitignore(line)
    assert errors == True

    line = ''
    errors = check_for_vscode_cache_in_gitignore(line)
    assert errors == False
