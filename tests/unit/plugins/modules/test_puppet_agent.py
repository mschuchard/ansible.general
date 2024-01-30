"""unit test for puppet agent module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import puppet_agent
from mschuchard.general.tests.unit.plugins.modules import utils


def test_puppet_agent_test_port(capfd):
    """test puppet agent with test and server port"""
    utils.set_module_args({'server_port': 8234, 'test': True})
    with pytest.raises(SystemExit, match='1'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'puppet:8234' in info['msg']
    assert info['return_code'] == 1
    assert 'agent' in info['cmd']
    assert '--serverport' in info['cmd']
    assert '-t' in info['cmd']


def test_puppet_agent_debug_noop_verbose(capfd):
    """test puppet agent with debug noop verbose"""
    utils.set_module_args({'debug': True, 'no_op': True, 'verbose': True})
    with pytest.raises(SystemExit, match='0'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'PID' in info['stderr']
    assert 'agent' in info['command']
    assert '-d' in info['command']
    assert '--noop' in info['command']
    assert '-v' in info['command']


def test_puppet_agent_nodaemonize_onetime(capfd):
    """test puppet agent nodaemonize onetime"""
    utils.set_module_args({'no_daemonize': True, 'onetime': True})
    with pytest.raises(SystemExit, match='1'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert len(info['msg']) == 0
    assert info['return_code'] == 1
    assert 'agent' in info['cmd']
    assert '--no-daemonize' in info['cmd']
    assert '--onetime' in info['cmd']
