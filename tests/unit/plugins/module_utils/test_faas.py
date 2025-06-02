"""unit test for faas module util"""

import pytest
from mschuchard.general.plugins.module_utils import faas


def test_faas_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported FaaS action attempted: foo'):
        faas.cmd(action='foo')

    # test warns on unknown flag, and discards unknown flag
    with pytest.warns(RuntimeWarning, match='Unsupported flag specified: foo'):
        assert faas.cmd(action='build', flags={'foo'}) == ['faas-cli', 'build']

    # test warns on unknown arg, and discards unknown arg
    with pytest.warns(RuntimeWarning, match='Unsupported FaaS arg specified: foo'):
        assert faas.cmd(action='logs', args={'foo': 'bar'}) == ['faas-cli', 'logs']

    # test warns on specifying args for action without corresponding args, and discards offending arg
    with pytest.warns(RuntimeWarning, match='Unsupported FaaS arg specified: foo'):
        assert faas.cmd(action='remove', args={'foo': 'bar'}) == ['faas-cli', 'remove']

    # test fails on nonexistent function file
    with pytest.raises(FileNotFoundError, match='Function config file does not exist or is invalid: /faas.yaml'):
        faas.cmd(action='build', args={'config_file': '/faas.yaml'})

    # test fails on function file with invalid yaml content
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        faas.cmd(action='deploy', args={'config_file': '.gitignore'})

    # test fails on soft parameter with invalid value
    with pytest.raises(ValueError, match='The "sort" parameter must be either "name" or "invocations"'):
        faas.cmd(action='list', args={'sort': 'invalid'})


def test_faas_cmd():
    """test various cmd returns"""


def test_ansible_to_faas_errors():
    """test various ansible_to_faas errors"""


def test_ansible_to_faas():
    """test various ansible_to_faas returns"""
