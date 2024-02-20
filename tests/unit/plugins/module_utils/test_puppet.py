"""unit test for puppet module util"""
__metaclass__ = type


import pytest
from mschuchard.general.plugins.module_utils import puppet


def test_puppet_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Puppet action attempted: foo'):
        puppet.cmd(action='foo')

    # test warns on unknown flag, and discards unknown flag
    with pytest.warns(RuntimeWarning, match='Unsupported Puppet flag specified: foo'):
        assert puppet.cmd(action='agent', flags=['foo']) == ['puppet', 'agent']

    # test warns on unknown arg, and discards unknown arg
    with pytest.warns(RuntimeWarning, match='Unsupported Puppet arg specified: foo'):
        assert puppet.cmd(action='agent', args={'foo': 'bar'}) == ['puppet', 'agent']

    # test warns on specifying args for action without corresponding args, and discards offending arg
    with pytest.warns(RuntimeWarning, match='Unsupported Puppet arg specified: foo'), pytest.raises(RuntimeError, match='Puppet manifest is not a file or does not exist: /home/matt/git_repos/mschuchard/general'):
        puppet.cmd(action='apply', args={'foo': 'bar'})

    # test fails on directory specified for manifest
    with pytest.raises(RuntimeError, match='Puppet manifest is not a file or does not exist: /home'):
        puppet.cmd(action='apply', manifest='/home')


def test_puppet_cmd():
    """test various cmd returns"""
    # test agent with no flags and no args
    assert puppet.cmd(action='agent') == ['puppet', 'agent']

    # test apply with test and noop
    assert puppet.cmd(action='apply', flags=['test', 'no_op'], manifest='/etc/group') == ['puppet', 'apply', '-t', '--noop', '/etc/group']

    # test agent with certname and serverport
    assert puppet.cmd(action='agent', args={'certname': 'example.domain', 'server_port': 1234}) == ['puppet', 'agent', '--certname', 'example.domain', '--serverport', '1234']
