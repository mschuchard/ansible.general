"""unit test for faas push module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import faas_push
from mschuchard.general.tests.unit.plugins.modules import utils


def test_faas_push_defaults(capfd):
    """test faas push with defaults"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml'})
    with pytest.raises(SystemExit, match='1'):
        faas_push.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'push' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_push_globals(capfd):
    """test faas push with filter and regex"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'filter': '*gif*', 'regex': 'fn[0-9]_.*'})
    with pytest.raises(SystemExit, match='1'):
        faas_push.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--filter' in info['cmd']
    assert '*gif*' in info['cmd']
    assert '--regex' in info['cmd']
    assert 'fn[0-9]_.*' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_push_parallel_tag_no_env_subst(capfd):
    """test faas push with parallel, tag, and without environment substitution"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'parallel': 4, 'tag': 'sha', 'env_subst': False})
    with pytest.raises(SystemExit, match='1'):
        faas_push.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--parallel' in info['cmd']
    assert '4' in info['cmd']
    assert '--tag' in info['cmd']
    assert 'sha' in info['cmd']
    assert '--envsubst=false' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']
