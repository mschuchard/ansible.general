"""unit test for terraform import module"""

import json

import pytest

from ansible_collections.mschuchard.general.plugins.modules import terraform_import
from ansible_collections.mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_import_defaults(capfd):
    """test terraform import with defaults"""
    utils.set_module_args({'address': 'aws_instance.this', 'id': 'i-1234567890'})
    with pytest.raises(SystemExit, match='1'):
        terraform_import.main()

    stdout, _ = capfd.readouterr()

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

    stdout, _ = capfd.readouterr()

    info = json.loads(stdout)
    assert f'-chdir={utils.fixtures_dir()}' in info['cmd']
    assert 'aws_instance.this' in info['cmd']
    assert 'aws_instance.this' == info['cmd'][-2]
    assert 'i-1234567890' in info['cmd']
    assert 'i-1234567890' == info['cmd'][-1]
    assert 'does not exist in the configuration.' in info['stderr']


def test_terraform_import_vars(capfd):
    """test terraform import with vars and var files"""
    utils.set_module_args(
        {
            'address': 'local_file.this',
            'id': '/path/to/local_file',
            'var': {'var_name': 'var_value', 'var_name_other': 'var_value_other'},
            'var_file': [f'{utils.fixtures_dir()}/foo.tfvars', f'{utils.fixtures_dir()}/foo.tfvars'],
        }
    )
    with pytest.raises(SystemExit, match='1'):
        terraform_import.main()

    stdout, _ = capfd.readouterr()

    info = json.loads(stdout)
    assert 'local_file.this' in info['cmd']
    assert 'local_file.this' == info['cmd'][-2]
    assert '/path/to/local_file' in info['cmd']
    assert '/path/to/local_file' == info['cmd'][-1]
    assert '-var' in info['cmd']
    assert "var_name='var_value'" in info['cmd']
    assert "var_name_other='var_value_other'" in info['cmd']
    assert f'-var-file={utils.fixtures_dir()}/foo.tfvars' in info['cmd']
    assert f'-var-file={utils.fixtures_dir()}/foo.tfvars' in info['cmd']
    assert 'No Terraform configuration files' in info['stderr']


def test_terraform_import_lock_lock_timeout(capfd):
    """test terraform import with lock disabled and lock timeout in ansible check mode"""
    utils.set_module_args(
        {
            'config_dir': str(utils.fixtures_dir()),
            'address': 'aws_instance.this',
            'id': 'i-1234567890',
            'lock': False,
            'lock_timeout': '1m',
            '_ansible_check_mode': True,
        }
    )
    with pytest.raises(SystemExit, match='0'):
        terraform_import.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert '-lock=false' in info['command']
    assert '-lock-timeout=1m' in info['command']
    # the lock args must not displace the positional address and id from the end of the command
    assert ['aws_instance.this', 'i-1234567890'] == info['command'][-2:]
    # ansible check mode exits before terraform executes
    assert 'stdout' not in info


def test_terraform_import_ignore_remote_version(capfd):
    """test terraform import with ignore remote version flag in ansible check mode"""
    utils.set_module_args({'address': 'aws_instance.this', 'id': 'i-1234567890', 'ignore_remote_version': True, '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_import.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-ignore-remote-version' in info['command']
    # flags precede the positional address and id
    assert info['command'].index('-ignore-remote-version') < info['command'].index('aws_instance.this')
    assert ['aws_instance.this', 'i-1234567890'] == info['command'][-2:]


def test_terraform_import_lock_defaults(capfd):
    """test terraform import omits lock args when lock parameters are unspecified in ansible check mode"""
    utils.set_module_args({'address': 'aws_instance.this', 'id': 'i-1234567890', '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_import.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    # the default of lock true is the terraform default, so no lock args or flags should be emitted
    assert not any(element.startswith('-lock') for element in info['command'])
    assert '-ignore-remote-version' not in info['command']
    assert ['aws_instance.this', 'i-1234567890'] == info['command'][-2:]
