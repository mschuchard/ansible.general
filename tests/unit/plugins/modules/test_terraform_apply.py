"""unit test for terraform apply module"""

import json

import pytest

from ansible_collections.mschuchard.general.plugins.modules import terraform_apply
from ansible_collections.mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_apply_defaults(capfd):
    """test terraform apply with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='1'):
        terraform_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'apply' in info['cmd']
    assert '-no-color' in info['cmd']
    assert '-input=false' in info['cmd']
    assert '-auto-approve' in info['cmd']
    assert 'Error: No configuration files' in info['stderr']


def test_terraform_apply_config_destroy(capfd):
    """test terraform apply with config and destroy"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir()), 'destroy': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert '-destroy' in info['command']
    assert 'No changes.' in info['stdout']


def test_terraform_apply_plan_file(capfd):
    """test terraform apply with plan_file"""
    utils.set_module_args({'plan_file': f'{utils.fixtures_dir()}/plan.tfplan'})
    with pytest.raises(SystemExit, match='1'):
        terraform_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert f'{utils.fixtures_dir()}/plan.tfplan' == info['cmd'][-1]
    assert 'Error: Saved plan does not match the given state' in info['stderr']


def test_terraform_apply_multiple_args(capfd):
    """test terraform apply with multiple arguments and a flag"""
    utils.set_module_args(
        {
            'target': ['aws_instance.this', 'local_file.that'],
            'var': {'var_name': 'var_value', 'var_name_other': 'var_value_other'},
            'var_file': [f'{utils.fixtures_dir()}/foo.tfvars', f'{utils.fixtures_dir()}/foo.tfvars'],
            'config_dir': str(utils.fixtures_dir()),
        }
    )
    with pytest.raises(SystemExit, match='0'):
        terraform_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    print(stdout)
    info = json.loads(stdout)
    assert not info['changed']
    assert '-target=aws_instance.this' in info['command']
    assert '-target=local_file.that' in info['command']
    assert '-var' in info['command']
    assert "var_name='var_value'" in info['command']
    assert "var_name_other='var_value_other'" in info['command']
    assert f'-var-file={utils.fixtures_dir()}/foo.tfvars' in info['command']
    assert f'-var-file={utils.fixtures_dir()}/foo.tfvars' in info['command']
    assert 'No changes.' in info['stdout']


def test_terraform_apply_lock_default(capfd):
    """test terraform apply does not disable the state lock by default"""
    utils.set_module_args({'_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-auto-approve' in info['command']
    assert '-lock=false' not in info['command']


def test_terraform_apply_lock_compact_warnings_parallelism(capfd):
    """test terraform apply with lock disabled, lock timeout, compact warnings, and parallelism"""
    utils.set_module_args(
        {
            'compact_warnings': True,
            'lock': False,
            'lock_timeout': '30s',
            'parallelism': 4,
            'config_dir': str(utils.fixtures_dir()),
            '_ansible_check_mode': True,
        }
    )
    with pytest.raises(SystemExit, match='0'):
        terraform_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert '-compact-warnings' in info['command']
    assert '-lock=false' in info['command']
    assert '-lock-timeout=30s' in info['command']
    assert '-parallelism=4' in info['command']


def test_terraform_apply_backup_state_state_out(capfd):
    """test terraform apply with backup disabled, and legacy local backend state paths"""
    utils.set_module_args(
        {
            'backup': '-',
            'state': f'{utils.fixtures_dir()}/in.tfstate',
            'state_out': f'{utils.fixtures_dir()}/out.tfstate',
            'config_dir': str(utils.fixtures_dir()),
            '_ansible_check_mode': True,
        }
    )
    with pytest.raises(SystemExit, match='0'):
        terraform_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-backup=-' in info['command']
    assert f'-state={utils.fixtures_dir()}/in.tfstate' in info['command']
    assert f'-state-out={utils.fixtures_dir()}/out.tfstate' in info['command']


@pytest.mark.parametrize(
    'param_name, param_value',
    [
        ('backup', '-'),
        ('compact_warnings', True),
        ('lock_timeout', '30s'),
        ('parallelism', 4),
        ('state', 'in.tfstate'),
        ('state_out', 'out.tfstate'),
    ],
)
def test_terraform_apply_plan_file_mutually_exclusive(capfd, param_name, param_value):
    """test terraform apply fails when plan_file is specified with a parameter that a saved plan does not accept"""
    utils.set_module_args({'plan_file': f'{utils.fixtures_dir()}/plan.tfplan', param_name: param_value})
    with pytest.raises(SystemExit, match='1'):
        terraform_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['failed']
    assert f'parameters are mutually exclusive: plan_file|{param_name}' in info['msg']
