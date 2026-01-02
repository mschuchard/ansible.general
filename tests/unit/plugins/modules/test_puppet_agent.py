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
    # sometimes stderr is empty on first execution for some reason
    if len(info['stderr']) > 0:
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
    assert 'agent' in info['cmd']
    assert '--no-daemonize' in info['cmd']
    assert '--onetime' in info['cmd']


def test_puppet_agent_logdest_sourceaddress(capfd):
    """test puppet agent with logdest and sourceaddress"""
    utils.set_module_args({'logdest': '/var/log/puppet/agent.log', 'sourceaddress': '192.168.1.100', 'onetime': True})
    with pytest.raises(SystemExit, match='1'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'agent' in info['cmd']
    assert '--logdest' in info['cmd']
    assert '/var/log/puppet/agent.log' in info['cmd']
    assert '--sourceaddress' in info['cmd']
    assert '192.168.1.100' in info['cmd']
    assert '--onetime' in info['cmd']


def test_puppet_agent_fingerprint_digest(capfd):
    """test puppet agent with fingerprint and digest"""
    utils.set_module_args({'fingerprint': True, 'digest': 'SHA1'})
    with pytest.raises(SystemExit, match='0'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'agent' in info['command']
    assert '--fingerprint' in info['command']
    assert '--digest' in info['command']
    assert 'SHA1' in info['command']


def test_puppet_agent_job_id_onetime(capfd):
    """test puppet agent with job_id and onetime"""
    utils.set_module_args({'job_id': 'ansible-run-12345', 'onetime': True})
    with pytest.raises(SystemExit, match='1'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'agent' in info['cmd']
    assert '--job-id' in info['cmd']
    assert 'ansible-run-12345' in info['cmd']
    assert '--onetime' in info['cmd']


def test_puppet_agent_disable(capfd):
    """test puppet agent disable with message"""
    utils.set_module_args({'disable': 'System maintenance in progress'})
    with pytest.raises(SystemExit, match='0'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['changed']
    assert 'agent' in info['command']
    assert '--disable' in info['command']
    assert 'System maintenance in progress' in info['command']


def test_puppet_agent_enable(capfd):
    """test puppet agent enable"""
    utils.set_module_args({'enable': True})
    with pytest.raises(SystemExit, match='0'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['changed']
    assert 'agent' in info['command']
    assert '--enable' in info['command']


def test_puppet_agent_evaltrace_trace(capfd):
    """test puppet agent with evaltrace and trace"""
    utils.set_module_args({'evaltrace': True, 'trace': True, 'onetime': True})
    with pytest.raises(SystemExit, match='1'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'agent' in info['cmd']
    assert '--evaltrace' in info['cmd']
    assert '--trace' in info['cmd']
    assert '--onetime' in info['cmd']


def test_puppet_agent_waitforcert(capfd):
    """test puppet agent with waitforcert"""
    utils.set_module_args({'waitforcert': 60, 'onetime': True})
    with pytest.raises(SystemExit, match='1'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'agent' in info['cmd']
    assert '--waitforcert' in info['cmd']
    assert '60' in info['cmd']
    assert '--onetime' in info['cmd']


def test_puppet_agent_certname(capfd):
    """test puppet agent with certname"""
    utils.set_module_args({'certname': 'custom.example.com', 'onetime': True})
    with pytest.raises(SystemExit, match='1'):
        puppet_agent.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'agent' in info['cmd']
    assert '--certname' in info['cmd']
    assert 'custom.example.com' in info['cmd']
    assert '--onetime' in info['cmd']
