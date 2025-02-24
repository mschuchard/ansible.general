"""unit test for packer fmt module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import packer_fmt
from mschuchard.general.tests.unit.plugins.modules import utils


def test_packer_fmt_defaults(capfd):
    """test packer fmt with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='0'):
        packer_fmt.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'fmt' in info['command']
    assert not info['stdout']


def test_packer_fmt_config_diff_write(capfd):
    """test packer fmt with config diff write"""
    utils.set_module_args({'diff': True, 'write': False, 'config_dir': str(utils.fixtures_dir())})
    with pytest.raises(SystemExit, match='0'):
        packer_fmt.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert str(utils.fixtures_dir()) == info['command'][-1]
    assert '-diff' in info['command']
    assert '-write=false' in info['command']
    assert '' == info['stdout']


def test_packer_fmt_recursive_check(capfd):
    """test packer fmt with upgrade"""
    utils.set_module_args({'check': True, 'recursive': True})
    with pytest.raises(SystemExit, match='0'):
        packer_fmt.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-check' in info['command']
    assert '-recursive' in info['command']
    assert not info['stdout']
