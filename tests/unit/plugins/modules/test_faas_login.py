"""unit test for faas login module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import faas_login
from mschuchard.general.tests.unit.plugins.modules import utils


def test_faas_login_defaults(capfd):
    """test faas login with defaults"""
    utils.set_module_args({'password': 'mypassword'})
    with pytest.raises(SystemExit, match='1'):
        faas_login.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'login' in info['cmd']
    assert '-u' in info['cmd']
    assert 'admin' in info['cmd']
    assert '-p' in info['cmd']
    assert (
        'Cannot connect to OpenFaaS on URL: http://127.0.0.1:8080. Get "http://127.0.0.1:8080/system/functions": dial tcp 127.0.0.1:8080: connect: connection refused'
        == info['stdout'].splitlines()[-1]
    )


def test_faas_login_username(capfd):
    """test faas login with custom username"""
    utils.set_module_args({'username': 'customuser', 'password': 'mypassword'})
    with pytest.raises(SystemExit, match='1'):
        faas_login.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '-u' in info['cmd']
    assert 'customuser' in info['cmd']
    assert '-p' in info['cmd']
    assert (
        'Cannot connect to OpenFaaS on URL: http://127.0.0.1:8080. Get "http://127.0.0.1:8080/system/functions": dial tcp 127.0.0.1:8080: connect: connection refused'
        == info['stdout'].splitlines()[-1]
    )


def test_faas_login_config_file_globals(capfd):
    """test faas login with config file and global parameters"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'password': 'mypassword', 'filter': '*gif*', 'regex': 'fn[0-9]_.*'})
    with pytest.raises(SystemExit, match='1'):
        faas_login.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--filter' in info['cmd']
    assert '*gif*' in info['cmd']
    assert '--regex' in info['cmd']
    assert 'fn[0-9]_.*' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '-u' in info['cmd']
    assert 'admin' in info['cmd']
    assert '-p' in info['cmd']
    assert (
        'Cannot connect to OpenFaaS on URL: http://127.0.0.1:8080. Get "http://127.0.0.1:8080/system/functions": dial tcp 127.0.0.1:8080: connect: connection refused'
        == info['stdout'].splitlines()[-1]
    )
