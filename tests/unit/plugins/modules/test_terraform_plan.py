"""unit test for terraform plan module"""

import json

import pytest

from ansible.module_utils import basic
from ansible_collections.mschuchard.general.plugins.modules import terraform_plan
from ansible_collections.mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_plan_defaults(capfd):
    """test terraform plan with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='1'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'plan' in info['cmd']
    assert '-no-color' in info['cmd']
    assert '-input=false' in info['cmd']
    assert 'Error: No configuration files' in info['stderr']


def test_terraform_plan_config_destroy(capfd):
    """test terraform plan with config and destroy"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir()), 'destroy': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert '-destroy' in info['command']
    assert 'No changes.' in info['stdout']


def test_terraform_plan_replace_out(capfd):
    """test terraform plan with replace and out"""
    utils.set_module_args({'replace': ['aws_instance.this', 'local_file.that'], 'out': 'plan.tfplan', 'config_dir': str(utils.fixtures_dir())})
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-replace=aws_instance.this' in info['command']
    assert '-replace=local_file.that' in info['command']
    assert '-out=plan.tfplan' in info['command']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert 'No changes.' in info['stdout']


def test_terraform_plan_multiple_args(capfd):
    """test terraform plan with multiple arguments and a flag"""
    utils.set_module_args(
        {
            'refresh_only': True,
            'var': {'var_name': 'var_value', 'var_name_other': 'var_value_other'},
            'var_file': [f'{utils.fixtures_dir()}/foo.tfvars', f'{utils.fixtures_dir()}/foo.tfvars'],
            'config_dir': str(utils.fixtures_dir()),
        }
    )
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-refresh-only' in info['command']
    assert '-var' in info['command']
    assert "var_name='var_value'" in info['command']
    assert "var_name_other='var_value_other'" in info['command']
    assert f'-var-file={utils.fixtures_dir()}/foo.tfvars' in info['command']
    assert f'-var-file={utils.fixtures_dir()}/foo.tfvars' in info['command']
    assert 'No changes.' in info['stdout']


def test_terraform_plan_compact_detailed_refresh(capfd, recwarn):
    """test terraform plan with compact warnings, detailed exitcode, and refresh disabled in ansible check mode"""
    utils.set_module_args({'compact_warnings': True, 'detailed_exitcode': True, 'refresh': False, '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-compact-warnings' in info['command']
    assert '-detailed-exitcode' in info['command']
    assert '-refresh=false' in info['command']
    # the refresh param defaults to true and must be popped before flag conversion, otherwise terraform.cmd warns about unsupported flags
    assert not any('Unsupported flag specified' in str(warning.message) for warning in recwarn)
    # ansible check mode exits before terraform executes
    assert 'stdout' not in info


def test_terraform_plan_lock_timeout_parallelism(capfd, recwarn):
    """test terraform plan with lock disabled, lock timeout, and parallelism in ansible check mode"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir()), 'lock': False, 'lock_timeout': '1m', 'parallelism': 4, '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert '-lock=false' in info['command']
    assert '-lock-timeout=1m' in info['command']
    assert '-parallelism=4' in info['command']
    assert not any('Unsupported flag specified' in str(warning.message) for warning in recwarn)


def test_terraform_plan_parallelism_zero(capfd):
    """test terraform plan passes a parallelism of zero instead of dropping the falsey value in ansible check mode"""
    utils.set_module_args({'parallelism': 0, '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '-parallelism=0' in info['command']


def test_terraform_plan_new_param_defaults(capfd, recwarn):
    """test terraform plan omits all new args and flags when the new parameters are unspecified in ansible check mode"""
    utils.set_module_args({'_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    # the defaults of lock and refresh true are the terraform defaults, so nothing beyond the base command should be emitted
    assert ['terraform', 'plan', '-no-color', '-input=false'] == info['command']
    assert not any('Unsupported flag specified' in str(warning.message) for warning in recwarn)


def test_terraform_plan_detailed_exitcode_diff(capfd, monkeypatch):
    """test terraform plan treats exit code 2 as success when detailed exitcode is enabled"""
    monkeypatch.setattr(basic.AnsibleModule, 'run_command', lambda module_instance, *args, **kwargs: (2, 'Plan: 1 to add, 0 to change, 0 to destroy.', ''))
    utils.set_module_args({'detailed_exitcode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    # a plan never modifies infrastructure, so a diff must not be reported as changed
    assert not info['changed']
    assert info['return_code'] == 2
    assert '-detailed-exitcode' in info['command']
    assert 'Plan: 1 to add' in info['stdout']


def test_terraform_plan_exitcode_diff_without_detailed(capfd, monkeypatch):
    """test terraform plan still fails on exit code 2 when detailed exitcode is not enabled"""
    monkeypatch.setattr(basic.AnsibleModule, 'run_command', lambda module_instance, *args, **kwargs: (2, '', 'unexpected failure'))
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='1'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['failed']
    assert info['return_code'] == 2
    assert '-detailed-exitcode' not in info['cmd']
    assert 'unexpected failure' in info['msg']
