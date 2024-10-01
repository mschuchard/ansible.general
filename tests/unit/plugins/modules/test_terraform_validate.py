"""unit test for terraform validate module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import terraform_validate
from mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_validate_defaults(capfd):
    """test terraform validate with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'validate' in info['command']
    assert '-no-color' in info['command']
    assert 'Success! The configuration is valid.' in info['stdout']


def test_terraform_validate_config(capfd):
    """test terraform validate with config"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir())})
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert f"-chdir={str(utils.fixtures_dir())}" in info['command']
    assert 'Success! The configuration is valid.' in info['stdout']


def test_terraform_validate_json_dir(capfd):
    """test terraform validate with json and test dir"""
    utils.set_module_args({'json': True, 'test_dir': 'my_tests'})
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '-json' in info['command']
    assert '-test-directory=my_tests' in info['command']
    assert 'Test directory does not exist' in info['stdout']
