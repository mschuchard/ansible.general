"""unit test for terraform test module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import terraform_test
from mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_test_defaults(capfd):
    """test terraform test with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'test' in info['command']
    assert 'Success! 0 passed, 0 failed.' in info['stdout']


def test_terraform_test_config(capfd):
    """test terraform test with config and test dir"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir()), 'test_dir': 'my_tests'})
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-test-directory=my_tests' in info['command']
    assert f"-chdir={str(utils.fixtures_dir())}" in info['command']
    assert 'Success! 0 passed, 0 failed.' in info['stdout']


def test_terraform_test_upgrade_backend(capfd):
    """test terraform test with json and vars"""
    utils.set_module_args({
        'json': True,
        'var': [{'var_name': 'var_value'}, {'var_name_other': 'var_value_other'}],
        'var_file': [f"{str(utils.fixtures_dir())}/foo.tfvars", f"{str(utils.fixtures_dir())}/foo.tfvars"]
    })
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-json' in info['command']
    assert '-var' in info['command']
    assert '\'var_name="var_value"\'' in info['command']
    assert '\'var_name_other="var_value_other"\'' in info['command']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.tfvars" in info['command']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.tfvars" in info['command']
    assert 'Success! 0 passed, 0 failed.' in info['stdout']
