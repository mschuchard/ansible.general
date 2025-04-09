"""unit test for terraform plan module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import terraform_plan
from mschuchard.general.tests.unit.plugins.modules import utils


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
    assert f"-chdir={str(utils.fixtures_dir())}" in info['command']
    assert '-destroy' in info['command']
    assert 'No changes.' in info['stdout']


def test_terraform_plan_replace_out(capfd):
    """test terraform plan with replace and out"""
    utils.set_module_args({
        'replace': ['aws_instance.this', 'local_file.that'],
        'out': 'plan.tfplan',
        'config_dir': str(utils.fixtures_dir())
    })
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-replace=aws_instance.this' in info['command']
    assert '-replace=local_file.that' in info['command']
    assert '-out=plan.tfplan' in info['command']
    assert f"-chdir={str(utils.fixtures_dir())}" in info['command']
    assert 'No changes.' in info['stdout']

def test_terraform_plan_multiple_args(capfd):
    """test terraform plan with multiple arguments and a flag"""
    utils.set_module_args({
        'refresh_only': True,
        'var': {'var_name': 'var_value', 'var_name_other': 'var_value_other'},
        'var_file': [f"{str(utils.fixtures_dir())}/foo.tfvars", f"{str(utils.fixtures_dir())}/foo.tfvars"],
        'config_dir': str(utils.fixtures_dir())
    })
    with pytest.raises(SystemExit, match='0'):
        terraform_plan.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-refresh-only' in info['command']
    assert '-var' in info['command']
    assert 'var_name=\'var_value\'' in info['command']
    assert 'var_name_other=\'var_value_other\'' in info['command']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.tfvars" in info['command']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.tfvars" in info['command']
    assert 'No changes.' in info['stdout']
