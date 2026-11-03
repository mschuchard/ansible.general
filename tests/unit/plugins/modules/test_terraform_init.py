"""unit test for terraform init module"""

import json

import pytest

from ansible_collections.mschuchard.general.plugins.modules import terraform_init
from ansible_collections.mschuchard.general.tests.unit.plugins.modules import utils


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
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
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
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert 'Terraform has been successfully initialized!' in info['stdout']


def test_terraform_init_multiple_args(capfd):
    """test terraform init with multiple arguments and a flag"""
    utils.set_module_args(
        {
            'migrate_state': True,
            'backend_config': [f'{utils.fixtures_dir()}/config.tf', {'scheme': 'https'}],
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
    assert f'-backend-config={utils.fixtures_dir()}/config.tf' in info['command']
    print(info['command'])
    assert "-backend-config='scheme=https'" in info['command']
    assert f'-plugin-dir={utils.fixtures_dir()}' in info['command']
    assert '-plugin-dir=/tmp' in info['command']
    assert 'Terraform initialized in an empty directory!' in info['stdout']


def test_terraform_init_from_module_get_lockfile_json(capfd):
    """test terraform init with from module, get disabled, lockfile, and json in ansible check mode"""
    utils.set_module_args({'from_module': '/path/to/source_module', 'get': False, 'lockfile': 'readonly', 'json': True, '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-from-module=/path/to/source_module' in info['command']
    assert '-get=false' in info['command']
    assert '-lockfile=readonly' in info['command']
    assert '-json' in info['command']
    # ansible check mode exits before terraform executes
    assert 'stdout' not in info


def test_terraform_init_reconfigure_lock_timeout_test_dir(capfd):
    """test terraform init with reconfigure, lock timeout, and test dir in ansible check mode"""
    utils.set_module_args({'reconfigure': True, 'lock_timeout': '1m', 'test_dir': 'my_tests', '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-reconfigure' in info['command']
    assert '-lock-timeout=1m' in info['command']
    assert '-test-directory=my_tests' in info['command']


def test_terraform_init_lock_ignore_remote_version(capfd, recwarn):
    """test terraform init with lock disabled and ignore remote version in ansible check mode"""
    utils.set_module_args(
        {'config_dir': str(utils.fixtures_dir()), 'backend': False, 'lock': False, 'get': False, 'ignore_remote_version': True, '_ansible_check_mode': True}
    )
    with pytest.raises(SystemExit, match='0'):
        terraform_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert '-backend=false' in info['command']
    assert '-lock=false' in info['command']
    assert '-get=false' in info['command']
    assert '-ignore-remote-version' in info['command']
    # the lock and get params default to true and must be popped before flag conversion, otherwise terraform.cmd warns about unsupported flags
    assert not any('Unsupported flag specified' in str(warning.message) for warning in recwarn)


def test_terraform_init_new_param_defaults(capfd, recwarn):
    """test terraform init omits all new args and flags when the new parameters are unspecified in ansible check mode"""
    utils.set_module_args({'_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    # the defaults of get and lock true are the terraform defaults, so nothing beyond the base command should be emitted
    assert ['terraform', 'init', '-no-color', '-input=false'] == info['command']
    assert not any('Unsupported flag specified' in str(warning.message) for warning in recwarn)
