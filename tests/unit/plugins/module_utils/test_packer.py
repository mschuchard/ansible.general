"""unit test for packer module util"""
__metaclass__ = type


import pytest
from ansible_collections.mschuchard.general.plugins.module_utils import packer


def test_packer_cmd_errors():
    pass


def test_packer_cmd():
    """test various packer_cmd returns"""

    # test init with no extra args
    assert packer.packer_cmd(action='init', args=[], target_dir='/home') == ['packer', 'init', '-machine-readable', '/home']

    # test fmt with check arg
    assert packer.packer_cmd(action='fmt', args=['check'], target_dir='/home') == ['packer', 'fmt', '-machine-readable', '-check', '/home']

    # test validate with default target_dir and ? args

    # test build with ?
