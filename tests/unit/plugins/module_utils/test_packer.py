"""unit test for packer module util"""
__metaclass__ = type


import pytest
from ansible_collections.mschuchard.general.plugins.module_utils import packer


def test_packer_cmd_errors():
    """test various packer_cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported Packer action attempted: foo'):
        packer.packer_cmd(action='foo', args=[], target_dir='.')

    # test fails on unknown arg or flag
    with pytest.raises(RuntimeError, match='Unknown Packer argument or flag specified: '):
        packer.packer_cmd(action='init', args=['foo'], target_dir='.')

    # test fails on nonexistent target_dir
    with pytest.raises(RuntimeError, match='Targeted directory or file does not exist: /1234567890'):
        packer.packer_cmd(action='init', args=[], target_dir='/1234567890')


def test_packer_cmd():
    """test various packer_cmd returns"""

    # test init with no extra args
    assert packer.packer_cmd(action='init', args=[], target_dir='/home') == ['packer', 'init', '-machine-readable', '/home']

    # test fmt with check arg
    assert packer.packer_cmd(action='fmt', args=['check'], target_dir='/home') == ['packer', 'fmt', '-machine-readable', '-check', '/home']

    # test validate with default target_dir and ? args

    # test build with ?
