"""unit test for terraform import module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import terraform_import
from mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_import_defaults(capfd):
    """test terraform import with defaults"""
    utils.set_module_args({'address': 'aws_instance.this', 'id': 'i-1234567890'})
    with pytest.raises(SystemExit, match='1'):
        terraform_import.main()

    stdout, stderr = capfd.readouterr()

    info = json.loads(stdout)
    assert 'import' in info['cmd']
    assert '-no-color' in info['cmd']
    assert '-input=false' in info['cmd']
    assert 'aws_instance.this' in info['cmd']
    assert 'aws_instance.this' == info['cmd'][-2]
    assert 'i-1234567890' in info['cmd']
    assert 'i-1234567890' == info['cmd'][-1]
    assert 'No Terraform configuration files' in info['stderr']


def test_terraform_import_config(capfd):
    """test terraform import with config"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir()), 'address': 'aws_instance.this', 'id': 'i-1234567890'})
    with pytest.raises(SystemExit, match='1'):
        terraform_import.main()

    stdout, stderr = capfd.readouterr()

    info = json.loads(stdout)
    assert f"-chdir={str(utils.fixtures_dir())}" in info['cmd']
    assert 'aws_instance.this' in info['cmd']
    assert 'aws_instance.this' == info['cmd'][-2]
    assert 'i-1234567890' in info['cmd']
    assert 'i-1234567890' == info['cmd'][-1]
    assert 'does not exist in the configuration.' in info['stderr']


def test_terraform_import_vars(capfd):
    """test terraform import with vars and var files"""
    utils.set_module_args({
        'address': 'local_file.this',
        'id': '/path/to/local_file',
        'var': {'var_name': 'var_value', 'var_name_other': 'var_value_other'},
        'var_file': [f"{str(utils.fixtures_dir())}/foo.tfvars", f"{str(utils.fixtures_dir())}/foo.tfvars"]
    })
    with pytest.raises(SystemExit, match='1'):
        terraform_import.main()

    stdout, stderr = capfd.readouterr()

    info = json.loads(stdout)
    assert 'local_file.this' in info['cmd']
    assert 'local_file.this' == info['cmd'][-2]
    assert '/path/to/local_file' in info['cmd']
    assert '/path/to/local_file' == info['cmd'][-1]
    assert '-var' in info['cmd']
    assert 'var_name=\'var_value\'' in info['cmd']
    assert 'var_name_other=\'var_value_other\'' in info['cmd']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.tfvars" in info['cmd']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.tfvars" in info['cmd']
    assert 'No Terraform configuration files' in info['stderr']
