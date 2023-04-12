"""unit test for goss module util"""
__metaclass__ = type


import pytest
from mschuchard.general.plugins.module_utils import goss


def test_goss_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported GoSS action attempted: foo'):
        goss.cmd(action='foo')

    # test fails on unknown flag
    with pytest.raises(RuntimeError, match='Unsupported GoSS flag specified: foo'):
        goss.cmd(action='render', flags=['foo'])

    # test fails on unknown arg
    with pytest.raises(RuntimeError, match='Unsupported GoSS arg specified: foo'):
        goss.cmd(action='validate', args={'foo': 'bar'})

    # test fails on specifying args for action without corresponding args
    with pytest.raises(RuntimeError, match='Unsupported GoSS arg specified: foo'):
        goss.cmd(action='render', args={'foo': 'bar'})

    # test fails on nonexistent target_dir
    with pytest.raises(FileNotFoundError, match='GoSSfile does not exist: /gossfile.yaml'):
        goss.cmd(action='render', gossfile='/gossfile.yaml')


def test_goss_cmd():
    """test various cmd returns"""
    # test render with no flags and no args
    assert goss.cmd(action='render', gossfile='/home') == ['goss', '-g', '/home', 'render']

    # test render with debug flag and no args
    assert goss.cmd(action='render', flags=['debug'], gossfile='/home') == ['goss', '-g', '/home', 'render', '--debug']

    # test validate with default gossfile, no flags, format and vars args
    assert goss.cmd(action='validate', args={'format': 'rspecish', 'vars': 'vars.yaml'}) == ['goss', '--vars', 'vars.yaml', 'validate', '--no-color', '-f', 'rspecish']

    # test serve with default gossfile, no flags, endpoint and port args
    assert goss.cmd(action='serve', args={'endpoint': 'https://example.com/goss', 'port': 8765}) == ['goss', 'serve', '-e', 'https://example.com/goss', '-l', ':8765']
