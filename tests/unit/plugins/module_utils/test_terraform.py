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
    with pytest.raises(RuntimeError, match='Targeted directory or file does not exist: /1234567890'):
        terraform.cmd(action='init', target_dir='/1234567890')

    # test fails on unsupported arg value type
    with pytest.raises(RuntimeError, match='Unexpected issue with argument name \'backend_config\' and argument value \'1\''):
        terraform.cmd(action='init', args={'backend_config': 1})

    # test fails on arg expecting value of list type and str type is provided
    with pytest.raises(RuntimeError, match='Unexpected issue with argument name \'backend_config\' and argument value \'foo\''):
        terraform.cmd(action='init', args={'backend_config': 'foo'})


def test_terraform_cmd():
    """test various cmd returns"""
    # test init with no flags and no args
    assert terraform.cmd(action='init', target_dir='/home') == ['terraform', 'init', '-no-color', '-input=false', '-chdir=/home']

    # test init with check flag and no args
    assert terraform.cmd(action='init', flags=['upgrade'], target_dir='/home') == ['terraform', 'init', '-no-color', '-input=false', '-upgrade', '-chdir=/home']

    # test init with default target_dir, no flags, backend and backend_config args
    assert terraform.cmd(action='init', args={'backend': 's3', 'backend_config': ['-backend-config=foo', '-backend-config=bar']}) == ['terraform', 'init', '-no-color', '-input=false', '-backend=s3', '-backend-config=foo', '-backend-config=bar', f"-chdir={str(Path.cwd())}"]

    # test init with force_copy and migrate_state flags, and plugin_dir args
    assert terraform.cmd(action='init', flags=['force_copy', 'migrate_state'], args={'plugin_dir': '/tmp'}, target_dir='/home') == ['terraform', 'init', '-no-color', '-input=false', '-force-copy', '-migrate-state', '-plugin-dir=/tmp', '-chdir=/home']
