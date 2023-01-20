"""unit test for packer module util"""
__metaclass__ = type


from pathlib import Path
import pytest
from mschuchard.general.plugins.module_utils import packer


def test_packer_cmd_errors():
    """test various packer_cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Packer action attempted: foo'):
        packer.packer_cmd(action='foo')

    # test fails on unknown flag
    with pytest.raises(RuntimeError, match='Unsupported Packer flag specified: foo'):
        packer.packer_cmd(action='init', flags=['foo'])

    # test fails on unknown arg
    with pytest.raises(RuntimeError, match='Unsupported Packer arg specified: foo'):
        packer.packer_cmd(action='validate', args={'foo': 'bar'})

    # test fails on action without args
    with pytest.raises(RuntimeError, match='Unsupported Packer arg specified: foo'):
        packer.packer_cmd(action='init', args={'foo': 'bar'})

    # test fails on nonexistent target_dir
    with pytest.raises(RuntimeError, match='Targeted directory or file does not exist: /1234567890'):
        packer.packer_cmd(action='init', target_dir='/1234567890')


def test_packer_cmd():
    """test various packer_cmd returns"""

    # test init with no flags and no args
    assert packer.packer_cmd(action='init', target_dir='/home') == ['packer', 'init', '-machine-readable', '-color=false', '/home']

    # test fmt with check flag and no args
    assert packer.packer_cmd(action='fmt', flags=['check'], target_dir='/home') == ['packer', 'fmt', '-machine-readable', '-color=false', '-check', '/home']

    # test validate with default target_dir, no flags, only and var args
    assert packer.packer_cmd(action='validate', args={'only': 'null.this,null.that', 'var': 'foo=bar'}) == ['packer', 'validate', '-machine-readable', '-color=false', '-only=null.this,null.that', '-var foo=bar', Path.cwd()]

    # test build with force and debug flags, and parallel builds args
    assert packer.packer_cmd(action='build', flags=['debug', 'force'], args={'parallel_builds': '1'}, target_dir='/home') == ['packer', 'build', '-machine-readable', '-color=false', '-debug', '-force', '-parallel-builds=1', '/home']
