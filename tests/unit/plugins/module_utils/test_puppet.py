"""unit test for puppet module util"""

import pytest
from pathlib import Path
from mschuchard.general.plugins.module_utils import puppet


def test_puppet_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Puppet action attempted: foo'):
        puppet.cmd(action='foo')

    # test warns on unknown flag, and discards unknown flag
    with pytest.warns(RuntimeWarning, match='Unsupported flag specified: foo'):
        assert puppet.cmd(action='agent', flags={'foo'}) == ['puppet', 'agent']

    # test warns on unknown arg, and discards unknown arg
    with pytest.warns(RuntimeWarning, match='Unsupported Puppet arg specified: foo'):
        assert puppet.cmd(action='agent', args={'foo': 'bar'}) == ['puppet', 'agent']

    # test warns on specifying args for action without corresponding args, and discards offending arg
    with (
        pytest.warns(RuntimeWarning, match='Unsupported Puppet arg specified: foo'),
    ):
        puppet.cmd(action='apply', args={'foo': 'bar'}, manifest=Path('/etc/group'))

    # test fails on directory specified for manifest
    with pytest.raises(FileNotFoundError, match='Puppet manifest is not a file or does not exist: /home'):
        puppet.cmd(action='apply', manifest=Path('/home'))

    # test fails on nonexistent catalog file
    with pytest.raises(FileNotFoundError, match='Puppet catalog file does not exist or is invalid: /nonexistent.json'):
        puppet.cmd(action='apply', catalog=Path('/nonexistent.json'))

    # test fails on function file with invalid yaml content
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        puppet.cmd(action='apply', catalog=Path('.gitignore'))

    # test fails on invalid server_port
    with pytest.raises(ValueError, match='Puppet server_port value must be between 1 and 65535: 0'):
        puppet.cmd(action='agent', args={'server_port': 0})

    # test fails when no manifest, execute, or catalog provided for apply
    with pytest.raises(RuntimeError, match='One of manifest, execute, or catalog must be provided for apply action'):
        puppet.cmd(action='apply')


def test_puppet_cmd():
    """test various cmd returns"""
    # test agent with no flags and no args
    assert puppet.cmd(action='agent') == ['puppet', 'agent']

    # test apply with test and noop
    assert set(puppet.cmd(action='apply', flags={'test', 'no_op'}, manifest=Path('/etc/group'))) == {'puppet', 'apply', '-t', '--noop', '/etc/group'}

    # test apply with execute
    assert puppet.cmd(action='apply', execute='notify { "test": }') == ['puppet', 'apply', '-e', 'notify { "test": }']

    # test agent with certname and serverport
    assert puppet.cmd(action='agent', args={'certname': 'example.domain', 'server_port': 1234, 'waitforcert': 60}) == [
        'puppet',
        'agent',
        '--certname',
        'example.domain',
        '--serverport',
        '1234',
        '--waitforcert',
        '60',
    ]
