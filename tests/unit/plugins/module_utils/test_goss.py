"""unit test for goss module util"""

from pathlib import Path

import pytest

from ansible_collections.mschuchard.general.plugins.module_utils import goss
from ansible_collections.mschuchard.general.tests.unit.plugins.modules import utils


def test_goss_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported GoSS action attempted: foo'):
        goss.cmd(action='foo')

    # test warns on unknown flag, and discards unknown flag
    with pytest.warns(RuntimeWarning, match='Unsupported flag specified: foo'):
        assert goss.cmd(action='render', flags={'foo'}) == ['goss', 'render']

    # test warns on unknown arg, and discards unknown arg
    with pytest.warns(RuntimeWarning, match='Unsupported GoSS arg specified: foo'):
        assert goss.cmd(action='validate', args={'foo': 'bar'}) == ['goss', 'validate', '--no-color']

    # test warns on specifying args for action without corresponding args, and discards offending arg
    with pytest.warns(RuntimeWarning, match='Unsupported GoSS arg specified: foo'):
        assert goss.cmd(action='render', args={'foo': 'bar'}) == ['goss', 'render']

    # test fails on nonexistent vars file
    with pytest.raises(FileNotFoundError, match='Vars file does not exist or is invalid: /foo'):
        goss.cmd(action='render', args={'vars': '/foo'})

    # test warns and fails on inline vars that are not valid json
    with (
        pytest.warns(
            SyntaxWarning,
            match="The vars_inline parameter values <module 'ansible_collections.mschuchard.general.plugins.module_utils.goss' from '.+/mschuchard/general/plugins/module_utils/goss.py'> could not be encoded to a JSON format string",
        ),
        pytest.raises(TypeError),
    ):
        goss.cmd(action='render', args={'vars_inline': goss})

    # test fails on nonexistent gossfile
    with pytest.raises(FileNotFoundError, match='GoSSfile does not exist or is invalid: /gossfile.yaml'):
        goss.cmd(action='render', gossfile=Path('/gossfile.yaml'))

    # test fails on invalid package parameter value
    with pytest.raises(ValueError, match='The specified parameter value for package chocolatey is not acceptable for GoSS'):
        goss.cmd(action='render', args={'package': 'chocolatey'})

    # test fails on gossfile with invalid yaml content
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        goss.cmd(action='render', gossfile=Path('.gitignore'))


def test_goss_cmd():
    """test various cmd returns"""
    # test render with no flags and no args
    assert goss.cmd(action='render', gossfile=Path('galaxy.yml')) == ['goss', '-g', 'galaxy.yml', 'render']

    # test render with debug flag and no args
    assert goss.cmd(action='render', flags={'debug'}, gossfile=Path('galaxy.yml')) == ['goss', '-g', 'galaxy.yml', 'render', '--debug']

    # test validate with default gossfile, no flags, format arg, and vars and package args
    assert goss.cmd(action='validate', args={'format': 'rspecish', 'vars': 'galaxy.yml', 'package': 'apk'}) == [
        'goss',
        '--vars',
        'galaxy.yml',
        '--package',
        'apk',
        'validate',
        '--no-color',
        '-f',
        'rspecish',
    ]

    # test validate with default gossfile, no flags, sleep arg, and vars_inline and max_concur action args
    assert goss.cmd(action='validate', args={'sleep': '5m', 'vars_inline': {'foo': 'bar'}, 'max_concur': 100}) == [
        'goss',
        '--vars-inline',
        '{"foo": "bar"}',
        'validate',
        '--no-color',
        '-s',
        '5m',
        '--max-concurrent',
        '100',
    ]

    # test serve with no flags, no global args, and action args
    assert goss.cmd(action='serve', args={'format': 'json'}) == ['goss', 'serve', '-f', 'json']

    # test serve with no flags, no global args, and cache and format_opts action args
    assert goss.cmd(action='serve', args={'format_opts': 'perfdata', 'cache': '1h'}) == ['goss', 'serve', '-o', 'perfdata', '-c', '1h']

    # test serve with default gossfile, no flags, endpoint and port args
    assert goss.cmd(action='serve', args={'log_level': 'info', 'endpoint': 'https://example.com/goss', 'port': 8765}) == [
        'goss',
        '-L',
        'INFO',
        'serve',
        '-e',
        'https://example.com/goss',
        '-l',
        ':8765',
    ]


def test_global_args_to_cmd_errors():
    """test various global_args_to_cmd errors"""
    # test fails on nonexistent vars file
    with pytest.raises(FileNotFoundError, match='Vars file does not exist or is invalid: /foo'):
        goss.global_args_to_cmd(gossfile=Path.cwd(), args={'vars': '/foo'})

    # test fails on vars file with invalid yaml/json content
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        goss.global_args_to_cmd(gossfile=Path.cwd(), args={'vars': '.gitignore'})

    # test warns and fails on inline vars that are not valid json
    with (
        pytest.warns(
            SyntaxWarning,
            match="The vars_inline parameter values <module 'ansible_collections.mschuchard.general.plugins.module_utils.goss' from '.+/mschuchard/general/plugins/module_utils/goss.py'> could not be encoded to a JSON format string",
        ),
        pytest.raises(TypeError),
    ):
        goss.global_args_to_cmd(gossfile=Path.cwd(), args={'vars_inline': goss})

    # test fails on invalid package parameter value
    with pytest.raises(ValueError, match='The specified parameter value for package chocolatey is not acceptable for GoSS'):
        goss.global_args_to_cmd(gossfile=Path.cwd(), args={'package': 'chocolatey'})

    # test fails on nonexistent gossfile
    with pytest.raises(FileNotFoundError, match='GoSSfile does not exist or is invalid: /gossfile.yaml'):
        goss.global_args_to_cmd(gossfile=Path('/gossfile.yaml'), args={})

    # test fails on gossfile with invalid yaml/json content
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        goss.global_args_to_cmd(gossfile=Path('.gitignore'), args={})


def test_global_args_to_cmd():
    """test various global_args_to_cmd returns"""
    # test empty args and default (cwd) gossfile produce an empty command
    assert goss.global_args_to_cmd(gossfile=Path.cwd(), args={}) == []

    # test log_level is uppercased in the command, and removed from args
    args: dict = {'log_level': 'info'}
    assert goss.global_args_to_cmd(gossfile=Path.cwd(), args=args) == ['-L', 'INFO']
    assert 'log_level' not in args

    # test valid vars file is included, and removed from args
    args = {'vars': f'{utils.fixtures_dir()}/goss.yaml'}
    assert goss.global_args_to_cmd(gossfile=Path.cwd(), args=args) == ['--vars', f'{utils.fixtures_dir()}/goss.yaml']
    assert 'vars' not in args

    # test vars_inline is json encoded, and removed from args
    args = {'vars_inline': {'foo': 'bar'}}
    assert goss.global_args_to_cmd(gossfile=Path.cwd(), args=args) == ['--vars-inline', '{"foo": "bar"}']
    assert 'vars_inline' not in args

    # test vars takes precedence over vars_inline (mutually exclusive at module level, but util processes vars first),
    # and vars_inline is left unprocessed/untouched in args since it is never reached
    args = {'vars': f'{utils.fixtures_dir()}/goss.yaml', 'vars_inline': {'foo': 'bar'}}
    assert goss.global_args_to_cmd(gossfile=Path.cwd(), args=args) == ['--vars', f'{utils.fixtures_dir()}/goss.yaml']
    assert 'vars' not in args
    assert 'vars_inline' in args

    # test package is included, and removed from args
    args = {'package': 'apk'}
    assert goss.global_args_to_cmd(gossfile=Path.cwd(), args=args) == ['--package', 'apk']
    assert 'package' not in args

    # test gossfile is included when not the default cwd
    assert goss.global_args_to_cmd(gossfile=Path('galaxy.yml'), args={}) == ['-g', 'galaxy.yml']

    # test gossfile is omitted when it equals the default cwd
    assert goss.global_args_to_cmd(gossfile=Path.cwd(), args={}) == []

    # test all global args combined in expected order, and unrelated args left untouched
    args = {'log_level': 'debug', 'vars_inline': {'my_service': 'httpd'}, 'package': 'rpm', 'format': 'json'}
    assert goss.global_args_to_cmd(gossfile=Path('galaxy.yml'), args=args) == [
        '-L',
        'DEBUG',
        '--vars-inline',
        '{"my_service": "httpd"}',
        '--package',
        'rpm',
        '-g',
        'galaxy.yml',
    ]
    # only the global args were consumed; unrelated keys remain for downstream action-arg handling
    assert args == {'format': 'json'}
