"""unit test for faas remove module"""

__metaclass__ = type


import json
import pytest
from ansible_collections.mschuchard.general.plugins.modules import faas_remove
from ansible_collections.mschuchard.general.tests.unit.plugins.modules import utils


def test_faas_remove_defaults(capfd):
    """test faas remove with defaults"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml'})
    with pytest.raises(SystemExit, match='1'):
        faas_remove.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'remove' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_remove_name(capfd):
    """test faas remove with function name"""
    utils.set_module_args({'name': 'url-ping'})
    with pytest.raises(SystemExit, match='1'):
        faas_remove.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'url-ping' == info['cmd'][-1]
    assert 'Delete "http://127.0.0.1:8080/system/functions": dial tcp 127.0.0.1:8080: connect: connection refused' in info['stdout']


def test_faas_remove_config_file_globals(capfd):
    """test faas remove with config file and global parameters"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'filter': '*gif*', 'regex': 'fn[0-9]_.*'})
    with pytest.raises(SystemExit, match='1'):
        faas_remove.main()

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


def test_faas_remove_gateway_tls_token(capfd):
    """test faas remove with gateway, tls_no_verify, and token"""
    utils.set_module_args({'name': 'url-ping', 'gateway': 'https://faas.example.com:8080', 'tls_no_verify': True, 'token': 'my-jwt-token'})
    with pytest.raises(SystemExit, match='1'):
        faas_remove.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'remove' in info['cmd']
    assert '-g' in info['cmd']
    assert 'https://faas.example.com:8080' in info['cmd']
    assert '--tls-no-verify' in info['cmd']
    assert '-k' in info['cmd']
    assert 'my-jwt-token' in info['cmd']
    assert 'url-ping' == info['cmd'][-1]


def test_faas_remove_namespace(capfd):
    """test faas remove with namespace"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'namespace': 'openfaas-fn'})
    with pytest.raises(SystemExit, match='1'):
        faas_remove.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'remove' in info['cmd']
    assert '-n' in info['cmd']
    assert 'openfaas-fn' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']


def test_faas_remove_env_subst_disabled(capfd):
    """test faas remove without environment substitution"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'env_subst': False})
    with pytest.raises(SystemExit, match='1'):
        faas_remove.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'remove' in info['cmd']
    assert '--envsubst=false' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']


def test_faas_remove_all_new_params(capfd):
    """test faas remove with all new parameters combined"""
    utils.set_module_args(
        {
            'name': 'url-ping',
            'gateway': 'https://faas.example.com:8080',
            'namespace': 'openfaas-fn',
            'tls_no_verify': True,
            'token': 'my-jwt-token',
            'env_subst': False,
        }
    )
    with pytest.raises(SystemExit, match='1'):
        faas_remove.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'remove' in info['cmd']
    assert '-g' in info['cmd']
    assert 'https://faas.example.com:8080' in info['cmd']
    assert '-n' in info['cmd']
    assert 'openfaas-fn' in info['cmd']
    assert '--tls-no-verify' in info['cmd']
    assert '-k' in info['cmd']
    assert 'my-jwt-token' in info['cmd']
    assert '--envsubst=false' in info['cmd']
    assert 'url-ping' == info['cmd'][-1]
