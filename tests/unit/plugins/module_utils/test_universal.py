"""unit test for universal module util"""


import pytest
from mschuchard.general.plugins.module_utils import universal


def test_validate_json_yaml_file():
    """test yaml and json file validator"""
    # test valid yaml file
    assert universal.validate_json_yaml_file('galaxy.yml')

    # test invalid yaml or json file
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        assert not universal.validate_json_yaml_file('.gitignore')


def test_vars_converter():
    """test ansible vars param to hashi cli converter"""
    # test accurate vars conversion
    assert universal.vars_converter([{'var1': 'value1'}, {'var2': 'value2'}, {'var3': 'value3'}]) == ['-var', 'var1=value1', '-var', 'var2=value2', '-var', 'var3=value3']


def test_var_files_converter():
    """test ansible var files param to hashi cli converter"""
    # test fails on missing var file
    with pytest.raises(FileNotFoundError, match='Var file does not exist: one.pkrvars.hcl'):
        universal.var_files_converter(['galaxy.yml', 'one.pkrvars.hcl'])

    # test accurate var files conversion
    assert universal.var_files_converter(['galaxy.yml', 'galaxy.yml', 'galaxy.yml']) == ['-var-file=galaxy.yml', '-var-file=galaxy.yml', '-var-file=galaxy.yml']
