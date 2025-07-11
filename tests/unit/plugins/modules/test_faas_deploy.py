"""unit test for faas deploy module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import faas_deploy
from mschuchard.general.tests.unit.plugins.modules import utils


def test_faas_deploy_defaults(capfd):
    """test faas deploy with defaults"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml'})
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'faas-cli' in info['cmd']
    assert 'deploy' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_replace_update_globals(capfd):
    """test faas deploy with replace, no update, and globals"""
    utils.set_module_args(
        {'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'replace': True, 'update': False, 'filter': '*gif*', 'regex': 'fn[0-9]_.*'}
    )
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    print(info)
    assert '--replace' in info['cmd']
    assert '--update=false' in info['cmd']
    assert '--filter' in info['cmd']
    assert '*gif*' in info['cmd']
    assert '--regex' in info['cmd']
    assert 'fn[0-9]_.*' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_annotation_label(capfd):
    """test faas deploy with annotation and label"""
    utils.set_module_args(
        {
            'config_file': f'{str(utils.fixtures_dir())}/stack.yaml',
            'annotation': {'imageregistry': 'docker.io', 'loadbalancer': 'mycloud'},
            'label': {'app': 'myapp', 'tier': 'backend'},
        }
    )
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    print(info)
    assert '--annotation' in info['cmd']
    assert 'imageregistry=docker.io' in info['cmd']
    assert 'loadbalancer=mycloud' in info['cmd']
    assert '--label' in info['cmd']
    assert 'app=myapp' in info['cmd']
    assert 'tier=backend' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']
