"""unit test for goss module util"""


import pytest
from mschuchard.general.plugins.module_utils import goss


def test_goss_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported GoSS action attempted: foo'):
        goss.cmd(action='foo')

    # test warns on unknown flag, and discards unknown flag
    with pytest.warns(RuntimeWarning, match='Unsupported GoSS flag specified: foo'):
        assert goss.cmd(action='render', flags=['foo']) == ['goss', 'render']

    # test warns on unknown arg, and discards unknown arg
    with pytest.warns(RuntimeWarning, match='Unsupported GoSS arg specified: foo'):
        assert goss.cmd(action='validate', args={'foo': 'bar'}) == ['goss', 'validate', '--no-color']

    # test warns on specifying args for action without corresponding args, and discards offending arg
    with pytest.warns(RuntimeWarning, match='Unsupported GoSS arg specified: foo'):
        assert goss.cmd(action='render', args={'foo': 'bar'}) == ['goss', 'render']

    # test fails on nonexistent vars file
    with pytest.raises(FileNotFoundError, match='Vars file does not exist: /foo'):
        goss.cmd(action='render', args={'vars': '/foo'})

    # test warns and fails on inline vars that are not valid json
    with pytest.warns(SyntaxWarning, match="The vars_inline parameter values <module 'mschuchard.general.plugins.module_utils.goss' from '.+/mschuchard/general/plugins/module_utils/goss.py'> could not be encoded to a JSON format string"), pytest.raises(TypeError):
        goss.cmd(action='render', args={'vars_inline': goss})

    # test fails on nonexistent gossfile
    with pytest.raises(FileNotFoundError, match='GoSSfile does not exist: /gossfile.yaml'):
        goss.cmd(action='render', gossfile='/gossfile.yaml')

    # test fails on invalid package parameter value
    with pytest.raises(ValueError, match='The specified parameter value for package chocolatey is not acceptable for GoSS'):
        goss.cmd(action='render', args={'package': 'chocolatey'})

    # test fails on gossfile with invalid yaml content
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        goss.cmd(action='render', gossfile='.gitignore')


def test_goss_cmd():
    """test various cmd returns"""
    # test render with no flags and no args
    assert goss.cmd(action='render', gossfile='galaxy.yml') == ['goss', '-g', 'galaxy.yml', 'render']

    # test render with debug flag and no args
    assert goss.cmd(action='render', flags=['debug'], gossfile='galaxy.yml') == ['goss', '-g', 'galaxy.yml', 'render', '--debug']

    # test validate with default gossfile, no flags, format arg, and vars and package args
    assert goss.cmd(action='validate', args={'format': 'rspecish', 'vars': 'galaxy.yml', 'package': 'apk'}) == ['goss', '--vars', 'galaxy.yml', '--package', 'apk', 'validate', '--no-color', '-f', 'rspecish']

    # test validate with default gossfile, no flags, sleep arg, and vars_inline and max_concur action args
    assert goss.cmd(action='validate', args={'sleep': '5m', 'vars_inline': {'foo': 'bar'}, 'max_concur': 100}) == ['goss', '--vars-inline', '{"foo": "bar"}', 'validate', '--no-color', '-s', '5m', '--max-concurrent', 100]

    # test serve with no flags, no global args, and action args
    assert goss.cmd(action='serve', args={'format': 'json'}) == ['goss', 'serve', '-f', 'json']

    # test serve with no flags, no global args, and cache and format_opts action args
    assert goss.cmd(action='serve', args={'format_opts': 'perfdata', 'cache': '1h'}) == ['goss', 'serve', '-o', 'perfdata', '-c', '1h']

    # test serve with default gossfile, no flags, endpoint and port args
    assert goss.cmd(action='serve', args={'endpoint': 'https://example.com/goss', 'port': 8765}) == ['goss', 'serve', '-e', 'https://example.com/goss', '-l', ':8765']
