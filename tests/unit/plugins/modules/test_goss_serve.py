__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import goss_serve
from mschuchard.general.tests.unit.plugins.modules import utils


def test_goss_serve_gossfile(capfd):
    """test goss serve with gossfile"""
    utils.set_module_args({'gossfile': '/tmp'})
    with pytest.raises(SystemExit, match='1'):
        goss_serve.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'serve' in info['cmd']
    assert '-g' in info['cmd']
    assert '/tmp' in info['cmd']
    assert '--vars' not in info['cmd']
    assert 'unknown file extension:' in info['stderr']


def test_goss_serve_format_vars(capfd):
    """test goss serve with format and vars"""
    utils.set_module_args({'format': 'json', 'vars': '/tmp'})
    with pytest.raises(SystemExit, match='1'):
        goss_serve.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'serve' in info['cmd']
    assert '-g' not in info['cmd']
    assert '-f' in info['cmd']
    assert 'json' in info['cmd']
    assert '--vars' in info['cmd']
    assert '/tmp' in info['cmd']
    assert 'failed while loading vars file "/tmp": Error: loading vars file \'/tmp\'\nread /tmp: is a directory' in info['stderr']


def test_goss_serve_endpoint_port(capfd):
    """test goss serve with endpoint and port"""
    utils.set_module_args({'endpoint': '/check', 'port': 8765})
    with pytest.raises(SystemExit, match='1'):
        goss_serve.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'serve' in info['cmd']
    assert '-e' in info['cmd']
    assert '/check' in info['cmd']
    assert '-l' in info['cmd']
    assert ':8765' in info['cmd']
    assert 'file error: open ./goss.yaml: no such file or directory' in info['stderr']
