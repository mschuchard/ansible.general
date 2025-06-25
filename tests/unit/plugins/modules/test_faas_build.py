"""unit test for faas build module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import faas_build
from mschuchard.general.tests.unit.plugins.modules import utils


def test_faas_build_defaults(capfd):
    """test faas build with defaults"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml'})
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'faas-cli' in info['cmd']
    assert 'build' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']
