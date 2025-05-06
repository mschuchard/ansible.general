"""unit test for faas module util"""

import pytest
from mschuchard.general.plugins.module_utils import faas


def test_faas_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported FaaS action attempted: foo'):
        faas.cmd(action='foo')

    # test fails on nonexistent function file
    with pytest.raises(FileNotFoundError, match='Function config file does not exist or is invalid: /faas.yaml'):
        faas.cmd(action='build', args={'config_file': '/faas.yaml'})

    # test fails on function file with invalid yaml content
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        faas.cmd(action='invoke', args={'config_file': '.gitignore'})


def test_faas_cmd():
    """test various cmd returns"""
