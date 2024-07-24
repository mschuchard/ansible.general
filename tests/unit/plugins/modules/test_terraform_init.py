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
    assert 'init' in info['command']
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
    assert f"-chdir={str(utils.fixtures_dir())}" in info['command']
    assert 'Terraform has been successfully initialized!' in info['stdout']
