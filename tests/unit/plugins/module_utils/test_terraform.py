"""unit test for terraform module util"""
__metaclass__ = type


from pathlib import Path
import pytest
from mschuchard.general.plugins.module_utils import terraform


# TODO more than init action
def test_terraform_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Terraform action attempted: foo'):
        terraform.cmd(action='foo')

    # test warns on unknown flag, and discards unknown flag
    with pytest.warns(RuntimeWarning, match='Unsupported Terraform flag specified: foo'):
        assert terraform.cmd(action='init', flags=['foo']) == ['terraform', 'init', '-no-color', '-input=false', f"-chdir={str(Path.cwd())}"]

    # test warns on unknown arg, and discards unknown arg
    with pytest.warns(RuntimeWarning, match='Unsupported Terraform arg specified: foo'):
        assert terraform.cmd(action='init', args={'foo': 'bar'}) == ['terraform', 'init', '-no-color', '-input=false', f"-chdir={str(Path.cwd())}"]

    # test warns on specifying args for action without corresponding args, and discards offending arg
    # TODO

    # test fails on nonexistent target_dir
    with pytest.raises(RuntimeError, match='Targeted directory does not exist: /1234567890'):
        terraform.cmd(action='init', target_dir='/1234567890')

    # test fails on unsupported arg value type
    with pytest.raises(RuntimeError, match='Unexpected issue with argument name \'backend_config\' and argument value \'1\''):
        terraform.cmd(action='init', args={'backend_config': 1})

    # test fails on arg expecting value of list type and str type is provided
    with pytest.raises(RuntimeError, match='Unexpected issue with argument name \'plugin_dir\' and argument value \'foo\''):
        terraform.cmd(action='init', args={'plugin_dir': 'foo'})


def test_terraform_cmd():
    """test various cmd returns"""
    # test init with no flags and no args
    assert terraform.cmd(action='init', target_dir='/home') == ['terraform', 'init', '-no-color', '-input=false', '-chdir=/home']

    # test init with check flag and no args
    assert terraform.cmd(action='init', flags=['upgrade'], target_dir='/home') == ['terraform', 'init', '-no-color', '-input=false', '-upgrade', '-chdir=/home']

    # test init with default target_dir, no flags, backend and backend_config args
    assert terraform.cmd(action='init', args={'backend': 'false', 'backend_config': ['-backend-config=foo', "-backend-config='bar=baz'"]}) == ['terraform', 'init', '-no-color', '-input=false', '-backend=false', '-backend-config=foo', "-backend-config='bar=baz'", f"-chdir={str(Path.cwd())}"]

    # test init with force_copy and migrate_state flags, and plugin_dir args
    assert terraform.cmd(action='init', flags=['force_copy', 'migrate_state'], args={'plugin_dir': ['-plugin-dir=/tmp', '-plugin-dir=/home']}, target_dir='/home') == ['terraform', 'init', '-no-color', '-input=false', '-force-copy', '-migrate-state', '-plugin-dir=/tmp', '-plugin-dir=/home', '-chdir=/home']


def test_ansible_to_terraform_errors():
    """test various ansible_to_terraform errors"""
    # test fails on nonexistent backend_config file argument value
    with pytest.raises(FileNotFoundError, match='Backend config file does not exist: /1234567890'):
        terraform.ansible_to_terraform(args={'backend_config': ['/1234567890']})

    # test warns on backend config list element with improper type
    with pytest.warns(RuntimeWarning, match='backend_config element value \'7\' is not a valid type; must be string for file path, or dict for key-value pair'):
        assert terraform.ansible_to_terraform(args={'backend_config': [7, 'galaxy.yml', {'foo':'bar'}]}) == {'backend_config': ['-backend-config=galaxy.yml', "-backend-config='foo=bar'"]}

    # test fails on nonexistent backend_config file argument value
    with pytest.raises(FileNotFoundError, match='Plugin directory does not exist: /1234567890'):
        terraform.ansible_to_terraform(args={'plugin_dir': ['/1234567890']})


def test_ansible_to_terraform():
    """test various ansible_to_terraform returns"""
    # test all possible args with multiple values
    assert terraform.ansible_to_terraform(args={
        'backend_config': ['galaxy.yml', {'foo':'bar'}],
        'plugin_dir': ['/tmp', '/home']
    }) == {
        'backend_config': ['-backend-config=galaxy.yml', "-backend-config='foo=bar'"],
        'plugin_dir': ['-plugin-dir=/tmp', '-plugin-dir=/home']
    }
