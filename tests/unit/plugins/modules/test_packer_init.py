__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import packer_init
from mschuchard.general.tests.unit.plugins.modules import utils


def test_packer_init_defaults(capfd):
    """test packer init with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='1'):
        packer_init.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['rc'] == 1
    assert 'init' in info['cmd']
    assert 'ui,error,Error: Could not find any config file in' in info['stdout']
