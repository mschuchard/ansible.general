"""unit test for terraform module util"""

import pytest
from pathlib import Path
from mschuchard.general.plugins.module_utils import terraform
from mschuchard.general.tests.unit.plugins.modules import utils


def test_terraform_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Terraform action attempted: foo'):
        terraform.cmd(action='foo')

    # test warns on unknown flag, and discards unknown flag
    with pytest.warns(RuntimeWarning, match='Unsupported flag specified: foo'):
        assert terraform.cmd(action='init', flags={'foo'}) == ['terraform', 'init', '-no-color', '-input=false']

    # test warns on unknown arg, and discards unknown arg
    with pytest.warns(RuntimeWarning, match='Unsupported Terraform arg specified: foo'):
        assert terraform.cmd(action='apply', args={'foo': 'bar'}) == ['terraform', 'apply', '-no-color', '-input=false', '-auto-approve']

    # test warns on specifying flags for action without corresponding flags, and discards offending flag
    with pytest.warns(RuntimeWarning, match='Unsupported flag specified: foo'):
        assert terraform.cmd(action='import', flags={'foo'}) == ['terraform', 'import', '-no-color', '-input=false']

    # test fails on nonexistent plan file
    with pytest.raises(RuntimeError, match='Targeted plan file or root module directory does not exist: /1234567890'):
        terraform.cmd(action='apply', target_dir=Path('/1234567890'))

    # test fails on nonexistent target_dir
    with pytest.raises(RuntimeError, match='Targeted root module directory does not exist: /1234567890'):
        terraform.cmd(action='init', target_dir=Path('/1234567890'))

    # test fails on unsupported arg value type
    with pytest.raises(RuntimeError, match="Unexpected issue with argument name 'backend_config' and argument value '1'"):
        terraform.cmd(action='init', args={'backend_config': 1})

    # test fails on arg expecting value of list type and str type is provided
    with pytest.raises(RuntimeError, match="Unexpected issue with argument name 'plugin_dir' and argument value 'foo'"):
        terraform.cmd(action='init', args={'plugin_dir': 'foo'})


def test_terraform_cmd():
    """test various cmd returns"""
    # test init with no flags and no args
    assert terraform.cmd(action='init', target_dir=Path('/home')) == ['terraform', '-chdir=/home', 'init', '-no-color', '-input=false']

    # test fmt with check flag and no args
    assert terraform.cmd(action='fmt', flags={'check'}, target_dir=Path('/home')) == ['terraform', '-chdir=/home', 'fmt', '-no-color', '-list=false', '-check']

    # test init with default target_dir, no flags, backend and backend_config args
    assert terraform.cmd(action='init', args={'backend': 'false', 'backend_config': ['-backend-config=foo', "-backend-config='bar=baz'"]}) == [
        'terraform',
        'init',
        '-no-color',
        '-input=false',
        '-backend=false',
        '-backend-config=foo',
        "-backend-config='bar=baz'",
    ]

    # test init with force_copy and migrate_state flags, and plugin_dir args
    assert set(
        terraform.cmd(
            action='init', flags={'force_copy', 'migrate_state'}, args={'plugin_dir': ['-plugin-dir=/tmp', '-plugin-dir=/home']}, target_dir=Path('/home')
        )
    ) == {'terraform', '-chdir=/home', 'init', '-no-color', '-input=false', '-force-copy', '-migrate-state', '-plugin-dir=/tmp', '-plugin-dir=/home'}

    # test bare apply with plan file
    assert terraform.cmd(action='apply', target_dir=Path(f'{str(utils.fixtures_dir())}/config.tf')) == [
        'terraform',
        'apply',
        '-no-color',
        '-input=false',
        '-auto-approve',
        f'{str(utils.fixtures_dir())}/config.tf',
    ]


def test_ansible_to_terraform_errors():
    """test various ansible_to_terraform errors"""
    # test fails on nonexistent backend_config file argument value
    with pytest.raises(FileNotFoundError, match='Backend config file does not exist: /1234567890'):
        terraform.ansible_to_terraform(args={'backend_config': ['/1234567890']})

    # test warns on backend config list element with improper type
    with pytest.warns(RuntimeWarning, match="backend_config element value '7' is not a valid type; must be string for file path, or dict for key-value pair"):
        args: dict = {'backend_config': [7, 'galaxy.yml', {'foo': 'bar'}]}
        terraform.ansible_to_terraform(args=args)
        assert args == {'backend_config': ['-backend-config=galaxy.yml', "-backend-config='foo=bar'"]}

    # test fails on nonexistent plugin_dir directory argument value
    with pytest.raises(FileNotFoundError, match='Plugin directory does not exist: /1234567890'):
        terraform.ansible_to_terraform(args={'plugin_dir': ['/1234567890']})


def test_ansible_to_terraform():
    """test various ansible_to_terraform returns"""
    # test all possible args with multiple values
    args: dict = {
        'backend_config': ['galaxy.yml', {'foo': 'bar'}],
        'filter': ['machine.tf', 'network.tf'],
        'plugin_dir': ['/tmp', '/home'],
        'replace': ['random.foo', 'local.bar'],
        # 'resources': {'resource.name':'resource.id', 'aws_instance.this':'i-1234567890'},
        'resource': {'resource.name': 'resource.id'},
        'target': ['random.foo', 'local.bar'],
        'var': {'var1': 'value1', 'var2': 'value2', 'var3': 'value3'},
        'var_file': ['galaxy.yml', 'galaxy.yml', 'galaxy.yml'],
    }
    terraform.ansible_to_terraform(args=args)
    assert args == {
        'backend_config': ['-backend-config=galaxy.yml', "-backend-config='foo=bar'"],
        'filter': ['-filter=machine.tf', '-filter=network.tf'],
        'plugin_dir': ['-plugin-dir=/tmp', '-plugin-dir=/home'],
        'replace': ['-replace=random.foo', '-replace=local.bar'],
        # 'resources': ['resource.name resource.id', 'aws_instance.this i-1234567890'],
        'resource': ['resource.name', 'resource.id'],
        'target': ['-target=random.foo', '-target=local.bar'],
        'var': ['-var', "var1='value1'", '-var', "var2='value2'", '-var', "var3='value3'"],
        'var_file': ['-var-file=galaxy.yml', '-var-file=galaxy.yml', '-var-file=galaxy.yml'],
    }
