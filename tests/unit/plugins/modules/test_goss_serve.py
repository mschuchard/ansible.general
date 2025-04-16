"""unit test for goss server module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import goss_serve
from mschuchard.general.tests.unit.plugins.modules import utils


def test_goss_serve_gossfile(capfd):
    """test goss serve with gossfile"""
    utils.set_module_args({'gossfile': 'galaxy.yml'})
    with pytest.raises(SystemExit, match='1'):
        goss_serve.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'serve' in info['cmd']
    assert '-g' in info['cmd']
    assert 'galaxy.yml' in info['cmd']
    assert '--vars' not in info['cmd']
    assert 'found 0 tests, source: galaxy.yml' in info['stderr']


def test_goss_serve_format_vars(capfd):
    """test goss serve with format and vars"""
    utils.set_module_args({'format': 'json', 'format_opts': 'pretty', 'vars': f'{str(utils.fixtures_dir())}/goss.yaml'})
    with pytest.raises(SystemExit, match='1'):
        goss_serve.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'serve' in info['cmd']
    assert '-g' not in info['cmd']
    assert '-f' in info['cmd']
    assert 'json' in info['cmd']
    assert '-o' in info['cmd']
    assert 'pretty' in info['cmd']
    assert '--vars' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/goss.yaml' in info['cmd']
    assert 'file error: open ./goss.yaml: no such file or directory' in info['stderr']


def test_goss_serve_endpoint_port(capfd):
    """test goss serve with cache, endpoint, and port"""
    utils.set_module_args({'cache': '1m', 'endpoint': '/check', 'port': 8765})
    with pytest.raises(SystemExit, match='1'):
        goss_serve.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'serve' in info['cmd']
    assert '-c' in info['cmd']
    assert '1m' in info['cmd']
    assert '-e' in info['cmd']
    assert '/check' in info['cmd']
    assert '-l' in info['cmd']
    assert ':8765' in info['cmd']
    assert 'file error: open ./goss.yaml: no such file or directory' in info['stderr']


def test_goss_serve_package_vars_inline(capfd):
    """test goss serve with package and inline vars"""
    utils.set_module_args({'package': 'rpm', 'vars_inline': {'my_service': 'httpd', 'my_package': 'apache'}})
    with pytest.raises(SystemExit, match='1'):
        goss_serve.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'serve' in info['cmd']
    assert '--package' in info['cmd']
    assert 'rpm' in info['cmd']
    assert '--vars-inline' in info['cmd']
    assert '{"my_service": "httpd", "my_package": "apache"}' in info['cmd']
    assert 'file error: open ./goss.yaml: no such file or directory' in info['stderr']
