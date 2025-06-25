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


def test_faas_build_no_cache_globals(capfd):
    """test faas build with no cache and globals"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'no_cache': True, 'filter': '*gif*', 'regex': 'fn[0-9]_.*'})
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--no-cache' in info['cmd']
    assert '--filter' in info['cmd']
    assert '*gif*' in info['cmd']
    assert '--regex' in info['cmd']
    assert 'fn[0-9]_.*' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_build_stack_pull_shrinkwrap(capfd):
    """test faas build with disable stack pull, pull, and shrinkwrap"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'disable_stack_pull': True, 'pull': True, 'shrinkwrap': True})
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--disable-stack-pull' in info['cmd']
    assert '--pull' in info['cmd']
    assert '--shrinkwrap' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']
