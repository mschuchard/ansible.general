"""unit test for puppet apply module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import puppet_apply
from mschuchard.general.tests.unit.plugins.modules import utils


def test_puppet_apply_test(capfd):
    """test puppet apply with test"""
    utils.set_module_args({'test': True, 'manifest': str(utils.fixtures_dir() / 'manifest.pp')})
    with pytest.raises(SystemExit, match='0'):
        puppet_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    print(info)
    assert info['changed']
    assert 'hello world' in info['stdout']
    assert not info['stderr']
    assert 'apply' in info['command']
    assert '-t' in info['command']
    assert str(utils.fixtures_dir() / 'manifest.pp') in info['command']


def test_puppet_apply_debug_noop_verbose(capfd):
    """test puppet apply with debug noop verbose"""
    utils.set_module_args({'debug': True, 'manifest': str(utils.fixtures_dir() / 'manifest.pp'), 'no_op': True, 'verbose': True})
    with pytest.raises(SystemExit, match='0'):
        puppet_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'hello world' in info['stdout']
    assert not info['stderr']
    assert 'apply' in info['command']
    assert '-d' in info['command']
    assert '--noop' in info['command']
    assert '-v' in info['command']
