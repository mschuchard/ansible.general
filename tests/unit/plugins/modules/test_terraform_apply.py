"""unit test for terraform apply module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import terraform_apply
from mschuchard.general.tests.unit.plugins.modules import utils


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
    assert f"-chdir={str(utils.fixtures_dir())}" in info['command']
    assert '-destroy' in info['command']
    assert 'No changes.' in info['stdout']


def test_terraform_apply_plan_file(capfd):
    """test terraform apply with plan_file"""
    utils.set_module_args({'plan_file': f"{str(utils.fixtures_dir())}/plan.tfplan"})
    with pytest.raises(SystemExit, match='1'):
        terraform_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert f"{str(utils.fixtures_dir())}/plan.tfplan" == info['cmd'][-1]
    assert 'Error: Saved plan does not match the given state' in info['stderr']

def test_terraform_apply_multiple_args(capfd):
    """test terraform apply with multiple arguments and a flag"""
    utils.set_module_args({
        'target': ['aws_instance.this', 'local_file.that'],
        'var': [{'var_name': 'var_value'}, {'var_name_other': 'var_value_other'}],
        'var_file': [f"{str(utils.fixtures_dir())}/foo.tfvars", f"{str(utils.fixtures_dir())}/foo.tfvars"],
        'config_dir': str(utils.fixtures_dir())
    })
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
    assert '\'var_name="var_value"\'' in info['command']
    assert '\'var_name_other="var_value_other"\'' in info['command']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.tfvars" in info['command']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.tfvars" in info['command']
    assert 'No changes.' in info['stdout']
