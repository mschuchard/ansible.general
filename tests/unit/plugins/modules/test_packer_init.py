"""unit test for packer init module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import packer_init
from mschuchard.general.tests.unit.plugins.modules import utils


def test_packer_init_defaults(capfd):
    """test packer init with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='1'):
        packer_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'init' in info['cmd']
    assert 'ui,error,Error: Could not find any config file in' in info['stdout']


def test_packer_init_config(capfd):
    """test packer init with config"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir())})
    with pytest.raises(SystemExit, match='0'):
        packer_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert str(utils.fixtures_dir()) == info['command'][-1]
    assert not info['stdout']


def test_packer_init_upgrade(capfd):
    """test packer init with upgrade"""
    utils.set_module_args({'upgrade': True, 'config_dir': str(utils.fixtures_dir())})
    with pytest.raises(SystemExit, match='0'):
        packer_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-upgrade' in info['command']
    assert str(utils.fixtures_dir()) == info['command'][-1]
    assert not info['stdout']
