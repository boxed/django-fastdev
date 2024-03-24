import subprocess
import pytest
from pathlib import Path
import sys
from django_fastdev.apps import FastDevVariableDoesNotExist, check_for_migrations_in_gitignore, check_for_pycache_in_gitignore, is_venv_ignored

def test_if_gitignore_has_migrations():
    line = 'migrations/'
    errors = check_for_migrations_in_gitignore(line)
    errors_expected = True
    assert errors == errors_expected


def test_if_gitignore_doesnt_have_migrations():
    line = 'not_migrations/'
    errors = check_for_migrations_in_gitignore(line)
    assert errors == False

@pytest.fixture
def git_repo(tmp_path: Path):
    subprocess.run(["git", "init", str(tmp_path)])
    return tmp_path

def test_is_venv_ignored_external_to_project(git_repo: Path):
    assert is_venv_ignored(git_repo) is True

@pytest.mark.parametrize('ignored', [True, False])
def test_is_venv_ignored_internal_to_project(monkeypatch, git_repo: Path, ignored: bool):
    (git_repo / "a-fake-venv").mkdir()

    if ignored:
        (git_repo / ".gitignore").write_text("a-fake-venv/")

    monkeypatch.setattr(sys, 'prefix', str(git_repo / "a-fake-venv"))

    assert is_venv_ignored(git_repo) is ignored

def test_is_venv_ignored_missing_git(monkeypatch, git_repo: Path):
    def mock_git_check_ignore(*args, **kwargs):
        raise FileNotFoundError

    # set the venv path inside the git repo so it tries to use git
    monkeypatch.setattr(sys, 'prefix', str(git_repo / "a-fake-venv"))
    monkeypatch.setattr(subprocess, 'run', mock_git_check_ignore)

    assert is_venv_ignored(git_repo) is None

def test_if_pycache_is_ignored_or_not():
    line = '__pycache__'
    errors = check_for_pycache_in_gitignore(line)
    assert errors == True

    line = ''
    errors = check_for_pycache_in_gitignore(line)
    assert errors == False
