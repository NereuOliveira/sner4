"""server functions tests"""

import os
import sys
from datetime import datetime
from io import StringIO
from unittest.mock import patch

import pytest

from sner.server import cli, get_dotted


def test_get_dotted_function():
    """test dotted access to the nested dictionary helper"""

    data = {'a': {'b': 1}}
    assert get_dotted(data, 'a') == {'b': 1}
    assert get_dotted(data, 'a.b') == 1
    assert get_dotted(data, 'a.b.c') is None


def test_datetime_filter(app):
    """test datetime jinja filter"""

    assert app.jinja_env.filters['datetime'](datetime.fromisoformat('2000-01-01T00:00:00')) == '2000-01-01T00:00:00'
    assert app.jinja_env.filters['datetime'](None) == ''


def test_cli():
    """test sner server cli/main flask wrapper"""

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch.object(sys, 'argv', []):
            with patch.object(os, 'environ', {}):
                cli()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


def test_shell():
    """test shell context imports"""

    buf_stdin = StringIO('print(db.session)\n')
    buf_stdout = StringIO()

    patch_argv = patch.object(sys, 'argv', ['bin/server', 'shell'])
    patch_environ = patch.object(os, 'environ', {})
    patch_stdin = patch.object(sys, 'stdin', buf_stdin)
    path_stdout = patch.object(sys, 'stdout', buf_stdout)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        with patch_argv, patch_environ, patch_stdin, path_stdout:
            cli()

    assert pytest_wrapped_e.value.code == 0
    assert 'sqlalchemy.orm.scoping.scoped_session' in buf_stdout.getvalue()
