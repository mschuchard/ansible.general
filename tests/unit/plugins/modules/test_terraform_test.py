"""unit test for terraform test module"""

import json

import pytest

from ansible_collections.mschuchard.general.plugins.modules import terraform_test
from ansible_collections.mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_test_defaults(capfd):
    """test terraform test with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert 'test' in info['command']
    assert 'Success! 0 passed, 0 failed.' in info['stdout']


def test_terraform_test_config(capfd):
    """test terraform test with config and test dir"""
    utils.set_module_args({'config_dir': str(utils.fixtures_dir()), 'test_dir': 'my_tests'})
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-test-directory=my_tests' in info['command']
    assert f'-chdir={utils.fixtures_dir()}' in info['command']
    assert 'Success! 0 passed, 0 failed.' in info['stdout']


def test_terraform_test_upgrade_backend(capfd):
    """test terraform test with json and vars"""
    utils.set_module_args(
        {
            'json': True,
            'var': {'var_name': 'var_value', 'var_name_other': 'var_value_other'},
            'var_file': [f'{utils.fixtures_dir()}/foo.tfvars', f'{utils.fixtures_dir()}/foo.tfvars'],
        }
    )
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-json' in info['command']
    assert '-var' in info['command']
    assert "var_name='var_value'" in info['command']
    assert "var_name_other='var_value_other'" in info['command']
    assert f'-var-file={utils.fixtures_dir()}/foo.tfvars' in info['command']
    assert f'-var-file={utils.fixtures_dir()}/foo.tfvars' in info['command']
    assert 'Success! 0 passed, 0 failed.' in info['stdout']


def test_terraform_test_verbose_parallelism_junit_xml(capfd, recwarn):
    """test terraform test with verbose, parallelism, and junit xml in ansible check mode"""
    utils.set_module_args({'verbose': True, 'parallelism': 4, 'junit_xml': 'report.xml', '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-verbose' in info['command']
    assert '-parallelism=4' in info['command']
    assert '-junit-xml=report.xml' in info['command']
    # the int parallelism must be converted to a str before terraform.cmd, otherwise a RuntimeError is raised and no warnings should surface
    assert not any('Unsupported' in str(warning.message) for warning in recwarn)
    # ansible check mode exits before terraform executes
    assert 'stdout' not in info


def test_terraform_test_parallelism_zero(capfd):
    """test terraform test passes a parallelism of zero instead of dropping the falsey value in ansible check mode"""
    utils.set_module_args({'parallelism': 0, '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '-parallelism=0' in info['command']


def test_terraform_test_cloud_run_filter(capfd):
    """test terraform test with cloud run and filter in ansible check mode"""
    utils.set_module_args({'cloud_run': 'app.terraform.io/example/module/aws', 'filter': ['one.tftest.hcl', 'two.tftest.hcl'], '_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert '-cloud-run=app.terraform.io/example/module/aws' in info['command']
    assert '-filter=one.tftest.hcl' in info['command']
    assert '-filter=two.tftest.hcl' in info['command']


def test_terraform_test_new_param_defaults(capfd, recwarn):
    """test terraform test omits all new args and flags when the new parameters are unspecified in ansible check mode"""
    utils.set_module_args({'_ansible_check_mode': True})
    with pytest.raises(SystemExit, match='0'):
        terraform_test.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    # none of the new parameters have a terraform default to emit, so nothing beyond the base command should appear
    assert ['terraform', 'test', '-no-color'] == info['command']
    assert not any('Unsupported' in str(warning.message) for warning in recwarn)


def test_terraform_test_cloud_run_junit_xml_exclusive(capfd):
    """test terraform test fails when cloud run and junit xml are both specified"""
    utils.set_module_args({'cloud_run': 'app.terraform.io/example/module/aws', 'junit_xml': 'report.xml'})
    with pytest.raises(SystemExit, match='1'):
        terraform_test.main()

    stdout, _ = capfd.readouterr()

    info = json.loads(stdout)
    assert info['failed']
    assert 'mutually exclusive' in info['msg']
    assert 'cloud_run' in info['msg']
    assert 'junit_xml' in info['msg']
