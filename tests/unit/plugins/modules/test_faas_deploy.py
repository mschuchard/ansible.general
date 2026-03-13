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
    assert 'deploy' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_replace_update_globals(capfd):
    """test faas deploy with replace, no update, and globals"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'strategy': 'replace', 'filter': '*gif*', 'regex': 'fn[0-9]_.*'})
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
            'strategy': 'replace',
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
    assert '--replace' in info['cmd']
    assert '--update=false' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_env_secret(capfd):
    """test faas deploy with environment variables and secrets"""
    utils.set_module_args(
        {'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'env': {'MYVAR': 'myval', 'DEBUG': 'true'}, 'secret': ['dockerhuborg', 'api-key']}
    )
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--env' in info['cmd']
    assert 'MYVAR=myval' in info['cmd']
    assert 'DEBUG=true' in info['cmd']
    assert '--secret' in info['cmd']
    assert 'dockerhuborg' in info['cmd']
    assert 'api-key' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_resource_limits(capfd):
    """test faas deploy with resource limits and requests"""
    utils.set_module_args(
        {
            'config_file': f'{str(utils.fixtures_dir())}/stack.yaml',
            'cpu_limit': '200m',
            'cpu_request': '100m',
            'memory_limit': '256Mi',
            'memory_request': '128Mi',
        }
    )
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--cpu-limit' in info['cmd']
    assert '200m' in info['cmd']
    assert '--cpu-request' in info['cmd']
    assert '100m' in info['cmd']
    assert '--memory-limit' in info['cmd']
    assert '256Mi' in info['cmd']
    assert '--memory-request' in info['cmd']
    assert '128Mi' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_tag(capfd):
    """test faas deploy with tag override"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'tag': 'sha'})
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--tag' in info['cmd']
    assert 'sha' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_direct_params(capfd):
    """test faas deploy with direct image and name parameters"""
    utils.set_module_args({'image': 'alexellis/faas-url-ping', 'name': 'url-ping', 'gateway': 'http://remote-site.com:8080'})
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--image' in info['cmd']
    assert 'alexellis/faas-url-ping' in info['cmd']
    assert '--name' in info['cmd']
    assert 'url-ping' in info['cmd']
    assert '--gateway' in info['cmd']
    assert 'http://remote-site.com:8080' in info['cmd']


def test_faas_deploy_constraint_readonly(capfd):
    """test faas deploy with constraints and readonly filesystem"""
    utils.set_module_args(
        {'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'constraint': ['node.role==worker', 'node.platform.os==linux'], 'readonly': True}
    )
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--constraint' in info['cmd']
    assert 'node.role==worker' in info['cmd']
    assert 'node.platform.os==linux' in info['cmd']
    assert '--readonly' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_tls_token_timeout(capfd):
    """test faas deploy with custom gateway, TLS, token, and timeout"""
    utils.set_module_args(
        {
            'config_file': f'{str(utils.fixtures_dir())}/stack.yaml',
            'gateway': 'https://faas.example.com:8080',
            'tls_no_verify': True,
            'token': 'my-jwt-token',
            'timeout': '2m',
        }
    )
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--gateway' in info['cmd']
    assert 'https://faas.example.com:8080' in info['cmd']
    assert '--tls-no-verify' in info['cmd']
    assert '--token' in info['cmd']
    assert 'my-jwt-token' in info['cmd']
    assert '--timeout' in info['cmd']
    assert '2m' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_handler_lang_network(capfd):
    """test faas deploy with handler, language, and network"""
    utils.set_module_args({'image': 'my_image', 'name': 'my_fn', 'handler': f'{str(utils.fixtures_dir())}', 'lang': 'python', 'network': 'func_functions'})
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--image' in info['cmd']
    assert 'my_image' in info['cmd']
    assert '--name' in info['cmd']
    assert 'my_fn' in info['cmd']
    assert '--handler' in info['cmd']
    assert str(utils.fixtures_dir()) in info['cmd']
    assert '--lang' in info['cmd']
    assert 'python' in info['cmd']
    assert '--network' in info['cmd']
    assert 'func_functions' in info['cmd']


def test_faas_deploy_namespace_fprocess(capfd):
    """test faas deploy with namespace and fprocess"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'namespace': 'openfaas-fn', 'fprocess': 'node index.js'})
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--namespace' in info['cmd']
    assert 'openfaas-fn' in info['cmd']
    assert '--fprocess' in info['cmd']
    assert 'node index.js' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_read_template_env_subst(capfd):
    """test faas deploy with read_template and env_subst disabled"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'read_template': False, 'env_subst': False})
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--read-template=false' in info['cmd']
    assert '--envsubst=false' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_deploy_all_new_params(capfd):
    """test faas deploy with all new parameters combined"""
    utils.set_module_args(
        {
            'config_file': f'{str(utils.fixtures_dir())}/stack.yaml',
            'env': {'KEY': 'val'},
            'secret': ['my-secret'],
            'constraint': ['node.role==worker'],
            'cpu_limit': '100m',
            'memory_request': '64Mi',
            'tag': 'branch',
            'namespace': 'openfaas-fn',
            'readonly': True,
            'tls_no_verify': True,
        }
    )
    with pytest.raises(SystemExit, match='1'):
        faas_deploy.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--env' in info['cmd']
    assert 'KEY=val' in info['cmd']
    assert '--secret' in info['cmd']
    assert 'my-secret' in info['cmd']
    assert '--constraint' in info['cmd']
    assert 'node.role==worker' in info['cmd']
    assert '--cpu-limit' in info['cmd']
    assert '100m' in info['cmd']
    assert '--memory-request' in info['cmd']
    assert '64Mi' in info['cmd']
    assert '--tag' in info['cmd']
    assert 'branch' in info['cmd']
    assert '--namespace' in info['cmd']
    assert 'openfaas-fn' in info['cmd']
    assert '--readonly' in info['cmd']
    assert '--tls-no-verify' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']
