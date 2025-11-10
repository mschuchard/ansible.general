"""unit test for faas list module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.tests.unit.plugins.modules import utils
from mschuchard.general.plugins.modules import faas_list


def test_faas_list_defaults(capfd):
    """test faas list with defaults"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml'})
    with pytest.raises(SystemExit, match='1'):
        faas_list.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'list' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_list_config_file(capfd):
    """test faas list with config file"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'filter': '*gif*', 'regex': 'fn[0-9]_.*'})
    with pytest.raises(SystemExit, match='1'):
        faas_list.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'faas-cli' in info['cmd']
    assert 'list' in info['cmd']
    assert '-f' in info['cmd']
    assert '--filter' in info['cmd']
    assert '*gif*' in info['cmd']
    assert '--regex' in info['cmd']
    assert 'fn[0-9]_.*' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_list_sort_invocations_verbose(capfd):
    """test faas list sorted by invocations"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'sort': 'invocations', 'verbose': True})
    with pytest.raises(SystemExit, match='1'):
        faas_list.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'faas-cli' in info['cmd']
    assert 'list' in info['cmd']
    assert '--sort' in info['cmd']
    assert 'invocations' in info['cmd']
    assert '-v' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']
