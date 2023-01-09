"""unit test for packer module util"""
__metaclass__ = type


import pytest
from pathlib import Path
from ansible_collections.mschuchard.general.plugins.module_utils import packer


def test_packer_cmd_errors():
    """test various packer_cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Packer action attempted: foo'):
        packer.packer_cmd(action='foo')

    # test fails on unknown arg or flag
    with pytest.raises(RuntimeError, match='Unknown Packer argument or flag specified: '):
        packer.packer_cmd(action='init', args=['foo'])

    # test fails on nonexistent target_dir
    with pytest.raises(RuntimeError, match='Targeted directory or file does not exist: /1234567890'):
        packer.packer_cmd(action='init', target_dir='/1234567890')


def test_packer_cmd():
    """test various packer_cmd returns"""

    # test init with no extra args
    assert packer.packer_cmd(action='init', args=[], target_dir='/home') == ['packer', 'init', '-machine-readable', '/home']

    # test fmt with check arg
    assert packer.packer_cmd(action='fmt', args=['check'], target_dir='/home') == ['packer', 'fmt', '-machine-readable', '-check', '/home']

    # TODO: test validate with default target_dir and ? args
    assert packer.packer_cmd(action='validate', args=[]) == ['packer', 'validate', '-machine-readable', Path.cwd()]

    # TODO: test build with ?
    assert packer.packer_cmd(action='build', args=[], target_dir='/home') == ['packer', 'build', '-machine-readable', '/home']
