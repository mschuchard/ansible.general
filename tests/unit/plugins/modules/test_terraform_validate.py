"""unit test for terraform validate module"""

import json

import pytest

from ansible_collections.mschuchard.general.plugins.modules import terraform_validate
from ansible_collections.mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_validate_defaults(capfd):
    """test terraform validate with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'validate' in info['command']
    assert '-no-color' in info['command']
    assert 'Success! The configuration is valid.' in info['stdout']


def test_terraform_validate_config(capfd):
    """test terraform validate with config"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir())})
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert 'Success! The configuration is valid.' in info['stdout']


def test_terraform_validate_json_dir(capfd):
    """test terraform validate with json and test dir"""
    utils.set_module_args({'json': True, 'test_dir': 'my_tests'})
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-json' in info['command']
    assert '-test-directory=my_tests' in info['command']
    assert 'Test directory does not exist' in info['stdout']


def test_terraform_validate_no_tests_query(capfd, recwarn):
    """test terraform validate with tests disabled and query in ansible check mode"""
    utils.set_module_args({'tests': False, 'query': True, '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-no-tests' in info['command']
    assert '-query' in info['command']
    # the tests param defaults to true and must be popped before flag conversion, otherwise terraform.cmd warns about unsupported flags
    assert not any('Unsupported flag specified' in str(warning.message) for warning in recwarn)
    # ansible check mode exits before terraform executes
    assert 'stdout' not in info


def test_terraform_validate_tests_enabled(capfd, recwarn):
    """test terraform validate omits the no tests flag when tests are explicitly enabled in ansible check mode"""
    utils.set_module_args({'tests': True, '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    # enabling tests is the terraform default, so the inverse flag must not be emitted
    assert '-no-tests' not in info['command']
    assert not any('Unsupported flag specified' in str(warning.message) for warning in recwarn)


def test_terraform_validate_new_param_defaults(capfd, recwarn):
    """test terraform validate omits all new args and flags when the new parameters are unspecified in ansible check mode"""
    utils.set_module_args({'_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    # the default of tests true is the terraform default, so nothing beyond the base command should be emitted
    assert ['terraform', 'validate', '-no-color'] == info['command']
    assert not any('Unsupported flag specified' in str(warning.message) for warning in recwarn)


def test_terraform_validate_all_params(capfd):
    """test terraform validate with config, json, no tests, query, and test dir in ansible check mode"""
    utils.set_module_args(
        {'config_dir': str(utils.fixtures_dir()), 'json': True, 'tests': False, 'query': True, 'test_dir': 'my_tests', '_ansible_check_mode': True}
    )
    with pytest.raises(SystemExit, match='0'):
        terraform_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert '-json' in info['command']
    assert '-no-tests' in info['command']
    assert '-query' in info['command']
    assert '-test-directory=my_tests' in info['command']
    # the chdir global option must precede the validate action
    assert info['command'].index(f'-chdir={utils.fixtures_dir()}') < info['command'].index('validate')
