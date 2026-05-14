"""unit test for faas logs module"""

__metaclass__ = type


import json
import pytest
from ansible_collections.mschuchard.general.plugins.modules import faas_logs
from ansible_collections.mschuchard.general.tests.unit.plugins.modules import utils


def test_faas_logs_defaults(capfd):
    """test faas logs with defaults"""
    utils.set_module_args({'name': 'my-function'})
    with pytest.raises(SystemExit, match='1'):
        faas_logs.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'logs' in info['cmd']
    assert 'my-function' in info['cmd']
    assert 'Cannot connect to OpenFaaS on URL: http://127.0.0.1:8080\n' == info['stdout']


def test_faas_logs_filter_regex(capfd):
    """test faas logs with instance flag and filter and regex"""
    utils.set_module_args({'name': 'my-function', 'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'filter': '*gif*', 'regex': 'fn[0-9]_.*'})
    with pytest.raises(SystemExit, match='1'):
        faas_logs.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--filter' in info['cmd']
    assert '*gif*' in info['cmd']
    assert '--regex' in info['cmd']
    assert 'fn[0-9]_.*' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert 'my-function' in info['cmd']
    assert 'Cannot connect to OpenFaaS on URL: http://127.0.0.1:8080\n' == info['stdout']


def test_faas_logs_name_instance(capfd):
    """test faas logs with instance flag"""
    utils.set_module_args({'name': 'my-function', 'instance': True})
    with pytest.raises(SystemExit, match='1'):
        faas_logs.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--instance' in info['cmd']
    assert 'my-function' == info['cmd'][-1]
    assert 'Cannot connect to OpenFaaS on URL: http://127.0.0.1:8080\n' == info['stdout']


def test_faas_logs_gateway_tls_token(capfd):
    """test faas logs with gateway, tls_no_verify, and token"""
    utils.set_module_args({'name': 'my-function', 'gateway': 'http://127.0.0.1:8080', 'tls_no_verify': True, 'token': 'my-jwt-token'})
    with pytest.raises(SystemExit, match='1'):
        faas_logs.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'logs' in info['cmd']
    assert '-g' in info['cmd']
    assert 'http://127.0.0.1:8080' in info['cmd']
    assert '--tls-no-verify' in info['cmd']
    assert '-k' in info['cmd']
    assert 'my-jwt-token' in info['cmd']
    assert 'my-function' == info['cmd'][-1]


def test_faas_logs_output_lines(capfd):
    """test faas logs with output format and lines"""
    utils.set_module_args({'name': 'my-function', 'output': 'json', 'lines': 5})
    with pytest.raises(SystemExit, match='1'):
        faas_logs.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'logs' in info['cmd']
    assert '-o' in info['cmd']
    assert 'json' in info['cmd']
    assert '--lines' in info['cmd']
    assert '5' in info['cmd']
    assert 'my-function' == info['cmd'][-1]


def test_faas_logs_since_no_tail(capfd):
    """test faas logs with since duration and tail disabled"""
    utils.set_module_args({'name': 'my-function', 'since': '10m', 'tail': False})
    with pytest.raises(SystemExit, match='1'):
        faas_logs.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'logs' in info['cmd']
    assert '--since' in info['cmd']
    assert '10m' in info['cmd']
    assert '--tail=false' in info['cmd']
    assert 'my-function' == info['cmd'][-1]


def test_faas_logs_namespace_print_name(capfd):
    """test faas logs with namespace and print_name flag"""
    utils.set_module_args({'name': 'my-function', 'namespace': 'openfaas-fn', 'print_name': True})
    with pytest.raises(SystemExit, match='1'):
        faas_logs.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'logs' in info['cmd']
    assert '-n' in info['cmd']
    assert 'openfaas-fn' in info['cmd']
    assert '--name' in info['cmd']
    assert 'my-function' == info['cmd'][-1]


def test_faas_logs_since_time_time_format(capfd):
    """test faas logs with since_time and time_format"""
    utils.set_module_args({'name': 'my-function', 'since_time': '2010-01-01T00:00:00Z', 'time_format': '2006-01-02T15:04:05Z07:00'})
    with pytest.raises(SystemExit, match='1'):
        faas_logs.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'logs' in info['cmd']
    assert '--since-time' in info['cmd']
    assert '2010-01-01T00:00:00Z' in info['cmd']
    assert '--time-format' in info['cmd']
    assert '2006-01-02T15:04:05Z07:00' in info['cmd']
    assert 'my-function' == info['cmd'][-1]
