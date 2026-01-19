"""unit test for puppet apply module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import puppet_apply
from mschuchard.general.tests.unit.plugins.modules import utils


def test_puppet_apply_test(capfd):
    """test puppet apply with test"""
    utils.set_module_args({'test': True, 'manifest': f'{str(utils.fixtures_dir())}/manifest.pp'})
    with pytest.raises(SystemExit, match='0'):
        puppet_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['changed']
    assert info['return_code'] == 2
    assert 'hello world' in info['stdout']
    assert not info['stderr']
    assert 'apply' in info['command']
    assert '-t' in info['command']
    assert f'{str(utils.fixtures_dir())}/manifest.pp' == info['command'][-1]


def test_puppet_apply_debug_noop_verbose(capfd):
    """test puppet apply with debug noop verbose"""
    utils.set_module_args({'debug': True, 'manifest': f'{str(utils.fixtures_dir())}/manifest.pp', 'no_op': True, 'verbose': True})
    with pytest.raises(SystemExit, match='0'):
        puppet_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert info['return_code'] == 0
    assert 'hello world' in info['stdout']
    assert not info['stderr']
    assert 'apply' in info['command']
    assert '-d' in info['command']
    assert '--noop' in info['command']
    assert '-v' in info['command']
    assert f'{str(utils.fixtures_dir())}/manifest.pp' == info['command'][-1]


def test_puppet_apply_execute(capfd):
    """test puppet apply with execute"""
    utils.set_module_args({'execute': 'notify { "hello world": }'})
    with pytest.raises(SystemExit, match='0'):
        puppet_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert info['return_code'] == 0
    assert 'hello world' in info['stdout']
    assert 'apply' in info['command']
    assert '-e' in info['command']
    assert 'notify { "hello world": }' in info['command']


def test_puppet_apply_detailed_exitcodes(capfd):
    """test puppet apply with detailed exitcodes"""
    utils.set_module_args({'detailed_exitcodes': True, 'manifest': f'{str(utils.fixtures_dir())}/manifest.pp'})
    with pytest.raises(SystemExit, match='0'):
        puppet_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['changed']
    assert info['return_code'] == 2
    assert 'hello world' in info['stdout']
    assert 'apply' in info['command']
    assert '--detailed-exitcodes' in info['command']
    assert f'{str(utils.fixtures_dir())}/manifest.pp' == info['command'][-1]


def test_puppet_apply_logdest(capfd):
    """test puppet apply with logdest"""
    utils.set_module_args({'logdest': '/var/log/puppet/apply.log', 'manifest': f'{str(utils.fixtures_dir())}/manifest.pp'})
    with pytest.raises(SystemExit, match='0'):
        puppet_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'apply' in info['command']
    assert '-l' in info['command']
    assert '/var/log/puppet/apply.log' in info['command']
    assert f'{str(utils.fixtures_dir())}/manifest.pp' == info['command'][-1]


def test_puppet_apply_loadclasses_write_catalog(capfd):
    """test puppet apply with loadclasses and write_catalog_summary"""
    utils.set_module_args({'loadclasses': True, 'write_catalog_summary': True, 'manifest': f'{str(utils.fixtures_dir())}/manifest.pp'})
    with pytest.raises(SystemExit, match='0'):
        puppet_apply.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'apply' in info['command']
    assert '-L' in info['command']
    assert '--write-catalog-summary' in info['command']
    assert f'{str(utils.fixtures_dir())}/manifest.pp' == info['command'][-1]
