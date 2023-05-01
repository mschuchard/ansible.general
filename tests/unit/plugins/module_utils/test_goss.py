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

    # test fails on nonexistent vars file
    with pytest.raises(FileNotFoundError, match='Vars file does not exist: /foo'):
        goss.cmd(action='render', args={'vars': '/foo'})

    # test fails on nonexistent gossfile
    with pytest.raises(FileNotFoundError, match='GoSSfile does not exist: /gossfile.yaml'):
        goss.cmd(action='render', gossfile='/gossfile.yaml')

    # test fails on gossfile with invalid yaml content
    with pytest.raises(RuntimeError, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'):
        goss.cmd(action='render', gossfile='.gitignore')


def test_goss_cmd():
    """test various cmd returns"""
    # test render with no flags and no args
    assert goss.cmd(action='render', gossfile='galaxy.yml') == ['goss', '-g', 'galaxy.yml', 'render']

    # test render with debug flag and no args
    assert goss.cmd(action='render', flags=['debug'], gossfile='galaxy.yml') == ['goss', '-g', 'galaxy.yml', 'render', '--debug']

    # test validate with default gossfile, no flags, format and vars args
    assert goss.cmd(action='validate', args={'format': 'rspecish', 'vars': 'galaxy.yml'}) == ['goss', '--vars', 'galaxy.yml', 'validate', '--no-color', '-f', 'rspecish']

    # test serve with default gossfile, no flags, endpoint and port args
    assert goss.cmd(action='serve', args={'endpoint': 'https://example.com/goss', 'port': 8765}) == ['goss', 'serve', '-e', 'https://example.com/goss', '-l', ':8765']
