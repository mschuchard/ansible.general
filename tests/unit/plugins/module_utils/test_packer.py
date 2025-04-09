"""unit test for packer module util"""


from pathlib import Path
import pytest
from mschuchard.general.plugins.module_utils import packer


def test_packer_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Packer action attempted: foo'):
        packer.cmd(action='foo')

    # test warns on unknown flag, and discards unknown flag
    with pytest.warns(RuntimeWarning, match='Unsupported flag specified: foo'):
        assert packer.cmd(action='init', flags=['foo']) == ['packer', 'init', '-machine-readable', str(Path.cwd())]

    # test warns on unknown arg, and discards unknown arg
    with pytest.warns(RuntimeWarning, match='Unsupported Packer arg specified: foo'):
        assert packer.cmd(action='validate', args={'foo': 'bar'}) == ['packer', 'validate', '-machine-readable', str(Path.cwd())]

    # test warns on specifying args for action without corresponding args, and discards offending arg
    with pytest.warns(RuntimeWarning, match='Unsupported Packer arg specified: foo'):
        assert packer.cmd(action='init', args={'foo': 'bar'}) == ['packer', 'init', '-machine-readable', str(Path.cwd())]

    # test fails on nonexistent target_dir
    with pytest.raises(RuntimeError, match='Targeted directory or file does not exist: /1234567890'):
        packer.cmd(action='init', target_dir='/1234567890')

    # test fails on unsupported arg value type
    with pytest.raises(RuntimeError, match='Unexpected issue with argument name \'var\' and argument value \'1\''):
        packer.cmd(action='validate', args={'var': 1})

    # test fails on arg expecting value of list type and str type is provided
    with pytest.raises(RuntimeError, match='Unexpected issue with argument name \'var\' and argument value \'foo\''):
        packer.cmd(action='validate', args={'var': 'foo'})


def test_packer_cmd():
    """test various cmd returns"""
    # test init with no flags and no args
    assert packer.cmd(action='init', target_dir='/home') == ['packer', 'init', '-machine-readable', '/home']

    # test fmt with check flag and no args
    assert packer.cmd(action='fmt', flags=['check'], target_dir='/home') == ['packer', 'fmt', '-machine-readable', '-check', '/home']

    # test validate with default target_dir, no flags, only and var args
    assert packer.cmd(action='validate', args={'only': 'null.this,null.that', 'var': ['-var', '\'foo="bar"\'']}) == ['packer', 'validate', '-machine-readable', '-only=null.this,null.that', '-var', '\'foo="bar"\'', str(Path.cwd())]

    # test build with force and debug flags, and parallel builds args
    assert packer.cmd(action='build', flags=['debug', 'force'], args={'parallel_builds': '1'}, target_dir='/home') == ['packer', 'build', '-machine-readable', '-color=false', '-debug', '-force', '-parallel-builds=1', '/home']


def test_ansible_to_packer_errors():
    """test various ansible_to_packer errors"""
    # test fails on unsupported on error argument value
    with pytest.raises(RuntimeError, match='Unsupported on error argument value specified: foo'):
        packer.ansible_to_packer(args={'on_error': 'foo'})

    # test fails on nonexistent var file
    with pytest.raises(FileNotFoundError, match='Var file does not exist: one.pkrvars.hcl'):
        packer.ansible_to_packer(args={'var_file': ['galaxy.yml', 'one.pkrvars.hcl']})


def test_ansible_to_packer():
    """test various ansible_to_packer returns"""
    # test all possible args with multiple values
    assert packer.ansible_to_packer(args={
        'excepts': ['foo', 'bar', 'baz'],
        'only': ['foo', 'bar', 'baz'],
        'on_error': 'cleanup',
        'parallel_builds': 2,
        'var': {'var1': 'value1', 'var2': 'value2', 'var3': 'value3'},
        'var_file': ['galaxy.yml', 'galaxy.yml', 'galaxy.yml']
    }) == {
        'excepts': 'foo,bar,baz',
        'only': 'foo,bar,baz',
        'on_error': 'cleanup',
        'parallel_builds': '2',
        'var': ['-var', 'var1=\'value1\'', '-var', 'var2=\'value2\'', '-var', 'var3=\'value3\''],
        'var_file': ['-var-file=galaxy.yml', '-var-file=galaxy.yml', '-var-file=galaxy.yml']
    }
