"""unit test for terraform init module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import terraform_init
from mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_init_defaults(capfd):
    """test terraform init with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='0'):
        terraform_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'init' in info['command']
    assert '-no-color' in info['command']
    assert '-input=false' in info['command']
    assert 'Terraform initialized in an empty directory!' in info['stdout']


def test_terraform_init_config(capfd):
    """test terraform init with config"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir())})
    with pytest.raises(SystemExit, match='0'):
        terraform_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['changed']
    assert f'-chdir={str(utils.fixtures_dir())}' in info['command']
    assert 'Terraform has been successfully initialized!' in info['stdout']


def test_terraform_init_upgrade_backend(capfd):
    """test terraform init with upgrade"""
    utils.set_module_args({'upgrade': True, 'backend': False, 'config_dir': str(utils.fixtures_dir())})
    with pytest.raises(SystemExit, match='0'):
        terraform_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['changed']
    assert '-upgrade' in info['command']
    assert f'-chdir={str(utils.fixtures_dir())}' in info['command']
    assert 'Terraform has been successfully initialized!' in info['stdout']


def test_terraform_init_multiple_args(capfd):
    """test terraform init with multiple arguments and a flag"""
    utils.set_module_args(
        {
            'migrate_state': True,
            'backend_config': [f'{str(utils.fixtures_dir())}/config.tf', {'scheme': 'https'}],
            'plugin_dir': [str(utils.fixtures_dir()), '/tmp'],
        }
    )
    with pytest.raises(SystemExit, match='0'):
        terraform_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-migrate-state' in info['command']
    assert f'-backend-config={str(utils.fixtures_dir())}/config.tf' in info['command']
    print(info['command'])
    assert "-backend-config='scheme=https'" in info['command']
    assert f'-plugin-dir={str(utils.fixtures_dir())}' in info['command']
    assert '-plugin-dir=/tmp' in info['command']
    assert 'Terraform initialized in an empty directory!' in info['stdout']
