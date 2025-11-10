"""unit test for faas logs module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import faas_logs
from mschuchard.general.tests.unit.plugins.modules import utils


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
    print(info)
    assert '--filter' in info['cmd']
    assert '*gif*' in info['cmd']
    assert '--regex' in info['cmd']
    assert 'fn[0-9]_.*' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert 'my-function' in info['cmd']
    assert 'Cannot connect to OpenFaaS on URL: http://127.0.0.1:8080\n' == info['stdout']


def test_faas_logs_name_instance(capfd):
    """test faas logs with name flag"""
    utils.set_module_args({'name': 'my-function', 'instance': True})
    with pytest.raises(SystemExit, match='1'):
        faas_logs.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    print(info)
    assert '--instance' in info['cmd']
    assert 'my-function' in info['cmd']
    assert 'Cannot connect to OpenFaaS on URL: http://127.0.0.1:8080\n' == info['stdout']
