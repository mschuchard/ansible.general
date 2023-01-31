"""unit test for packer module util"""
__metaclass__ = type


from pathlib import Path
import pytest
from mschuchard.general.plugins.module_utils import packer


def test_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Packer action attempted: foo'):
        packer.cmd(action='foo')

    # test fails on unknown flag
    with pytest.raises(RuntimeError, match='Unsupported Packer flag specified: foo'):
        packer.cmd(action='init', flags=['foo'])

    # test fails on unknown arg
    with pytest.raises(RuntimeError, match='Unsupported Packer arg specified: foo'):
        packer.cmd(action='validate', args={'foo': 'bar'})

    # test fails on specifying args for action without corresponding args
    with pytest.raises(RuntimeError, match='Unsupported Packer arg specified: foo'):
        packer.cmd(action='init', args={'foo': 'bar'})

    # test fails on nonexistent target_dir
    with pytest.raises(RuntimeError, match='Targeted directory or file does not exist: /1234567890'):
        packer.cmd(action='init', target_dir='/1234567890')


def test_cmd():
    """test various cmd returns"""
    # test init with no flags and no args
    assert packer.cmd(action='init', target_dir='/home') == ['packer', 'init', '-machine-readable', '-color=false', '/home']

    # test fmt with check flag and no args
    assert packer.cmd(action='fmt', flags=['check'], target_dir='/home') == ['packer', 'fmt', '-machine-readable', '-color=false', '-check', '/home']

    # test validate with default target_dir, no flags, only and var args
    assert packer.cmd(action='validate', args={'only': 'null.this,null.that', 'var': 'foo=bar'}) == ['packer', 'validate', '-machine-readable', '-color=false', '-only=null.this,null.that', '-var foo=bar', str(Path.cwd())]

    # test build with force and debug flags, and parallel builds args
    assert packer.cmd(action='build', flags=['debug', 'force'], args={'parallel_builds': '1'}, target_dir='/home') == ['packer', 'build', '-machine-readable', '-color=false', '-debug', '-force', '-parallel-builds=1', '/home']


def test_ansible_to_packer_errors():
    """test various ansible_to_packer errors"""
    # test fails on unsupported on error argument value
    with pytest.raises(RuntimeError, match='Unsupported on error argument value specified: foo'):
        packer.ansible_to_packer(args={'on_error': 'foo'})

    # test fails on unsupported on error argument value
    with pytest.raises(RuntimeError, match='Unsupported Packer arg specified: foo'):
        packer.ansible_to_packer(args={'foo': 'bar'})


def test_ansible_to_packer():
    """test various ansible_to_packer returns"""
    # test all possible args with multiple values
    assert packer.ansible_to_packer(args={
        'except': ['foo', 'bar', 'baz'],
        'only': ['foo', 'bar', 'baz'],
        'on_error': 'cleanup',
        'parallel_builds': 2,
        'var': [{'var1': 'value1'}, {'var2': 'value2'}, {'var3': 'value3'}],
        'var_file': ['one.pkrvars.hcl', 'two.pkrvars.hcl', 'three.pkrvars.hcl']
    }) == {
        'except': 'foo,bar,baz',
        'only': 'foo,bar,baz',
        'on_error': 'cleanup',
        'parallel_builds': '2',
        'var': 'var1=value1 -var var2=value2 -var var3=value3',
        'var_file': 'one.pkrvars.hcl -var-file=two.pkrvars.hcl -var-file=three.pkrvars.hcl'
    }
