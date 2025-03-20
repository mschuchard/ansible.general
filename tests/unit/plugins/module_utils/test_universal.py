"""unit test for universal module util"""


import pytest
from pathlib import Path
from mschuchard.general.plugins.module_utils import universal


def test_validate_json_yaml_file():
    """test yaml and json file validator"""
    # test valid yaml file
    assert universal.validate_json_yaml_file('galaxy.yml')

    # test invalid yaml or json file
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        assert not universal.validate_json_yaml_file('.gitignore')


def test_action_flags_command():
    """test action flags dict to list of command strings converter"""
    # test accurate flags conversion
    assert universal.action_flags_command(['hello'], ['foo', 'bar'], {'foo': '--foo', 'bar': '--bar'}) == ['hello', '--foo', '--bar']

    # test unsupported flag input
    with pytest.warns(RuntimeWarning, match='Unsupported flag specified: baz'):
        assert universal.action_flags_command(['hello'], ['foo', 'baz'], {'foo': '--foo', 'bar': '--bar'}) == ['hello', '--foo']

    # test action with no action flags input
    with pytest.warns(RuntimeWarning, match='Unsupported flag specified: foo'):
        assert universal.action_flags_command(['hello'], ['foo'], {}) == ['hello']


def test_vars_converter():
    """test ansible vars param to hashi cli converter"""
    # test accurate vars conversion
    assert universal.vars_converter([{'var1': 'value1'}, {'var2': 'value2'}, {'var3': 'value3'}]) == ['-var', 'var1=\'value1\'', '-var', 'var2=\'value2\'', '-var', 'var3=\'value3\'']

    # test with complex types
    assert universal.vars_converter([{'var1': ['value1', 'value2']}, {'var2': {'foo': 'bar', 'baz': 'bot'}}]) == ['-var', 'var1=\'["value1","value2"]\'', '-var', 'var2=\'{"foo":"bar","baz":"bot"}\'']


def test_var_files_converter():
    """test ansible var files param to hashi cli converter"""
    # test fails on missing var file
    with pytest.raises(FileNotFoundError, match='Var file does not exist: one.pkrvars.hcl'):
        universal.var_files_converter(['galaxy.yml', 'one.pkrvars.hcl'])

    # test accurate var files conversion
    assert universal.var_files_converter(['galaxy.yml', 'galaxy.yml', 'galaxy.yml']) == ['-var-file=galaxy.yml', '-var-file=galaxy.yml', '-var-file=galaxy.yml']


def test_params_to_flags_args():
    """test ansible module params to utils flags and args converter"""

    params: dict = {
        'foo': 'bar',
        'baz': True,
        'none': None,
        'path': '/tmp',
    }
    spec: dict[str, dict] = {
        'baz': {'type': 'bool', 'required': False},
        'foo': {'type': 'str', 'required': False, 'default': 'maybe'},
        'none': {'type': 'int', 'required': False},
        'path': {'type': 'path', 'required': False, 'default': Path.cwd()},
    }

    assert universal.params_to_flags_args(params, spec) == (['baz'], {'foo': 'bar', 'path': Path('/tmp')})
