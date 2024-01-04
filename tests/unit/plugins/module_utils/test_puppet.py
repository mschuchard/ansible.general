"""unit test for puppet module util"""
__metaclass__ = type


from pathlib import Path
import pytest
from mschuchard.general.plugins.module_utils import puppet


def test_puppet_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Puppet action attempted: foo'):
        puppet.cmd(action='foo')

    # test fails on unknown flag
    with pytest.raises(RuntimeError, match='Unsupported Puppet flag specified: foo'):
        puppet.cmd(action='agent', flags=['foo'])

    # test fails on unknown arg
    with pytest.raises(RuntimeError, match='Unsupported Puppet arg specified: foo'):
        puppet.cmd(action='agent', args={'foo': 'bar'})


def test_puppet_cmd():
    """test various cmd returns"""
    # test agent with no flags and no args
    assert puppet.cmd(action='agent') == ['puppet', 'agent']

    # test agent with test and noop
    assert puppet.cmd(action='agent', flags=['test', 'no_op']) == ['puppet', 'agent', '-t', '--noop']

    # test agent with certname and serverport
    assert puppet.cmd(action='agent', args={'certname': 'example.domain', 'server_port': 1234}) == ['puppet', 'agent', '--certname', 'example.domain', '--serverport', '1234']
