"""unit test for terraform fmt module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import terraform_fmt
from mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_fmt_defaults(capfd):
    """test terraform fmt with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='0'):
        terraform_fmt.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'fmt' in info['command']
    assert '-no-color' in info['command']
    assert '-list=false' in info['command']
    assert '' ==  info['stdout']


def test_terraform_fmt_config_diff_write(capfd):
    """test terraform fmt with config diff write"""
    utils.set_module_args({'diff': True, 'write': False, 'config_dir': str(utils.fixtures_dir())})
    with pytest.raises(SystemExit, match='0'):
        terraform_fmt.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert f"-chdir={str(utils.fixtures_dir())}" in info['command']
    assert '-diff' in info['command']
    assert '-write=false' in info['command']
    assert '' == info['stdout']


def test_terraform_fmt_check_recursive(capfd):
    """test terraform validate with check recursive"""
    utils.set_module_args({'check': True, 'recursive': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_fmt.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-check' in info['command']
    assert '-recursive' in info['command']
    assert '' == info['stdout']
