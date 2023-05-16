"""unit test for goss validate module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import goss_validate
from mschuchard.general.tests.unit.plugins.modules import utils


def test_goss_validate_gossfile(capfd):
    """test goss validate with gossfile"""
    utils.set_module_args({'gossfile': 'galaxy.yml'})
    with pytest.raises(SystemExit, match='1'):
        goss_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'validate' in info['cmd']
    assert '-g' in info['cmd']
    assert 'galaxy.yml' in info['cmd']
    assert 'Error: found 0 tests, source: galaxy.yml\n' == info['stdout']


def test_goss_validate_format_vars(capfd):
    """test goss validate with format and vars"""
    utils.set_module_args({'format': 'json', 'vars': 'galaxy.yml'})
    with pytest.raises(SystemExit, match='1'):
        goss_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'validate' in info['cmd']
    assert '-g' not in info['cmd']
    assert '-f' in info['cmd']
    assert 'json' in info['cmd']
    assert '--vars' in info['cmd']
    assert 'galaxy.yml' in info['cmd']
    assert 'Error: file error: open ./goss.yaml: no such file or directory\n' == info['stdout']


def test_goss_validate_package_vars_inline(capfd):
    """test goss validate with package and inline vars"""
    utils.set_module_args({'package': 'dpkg', 'vars_inline': {'my_service': 'httpd', 'my_package': 'apache'}})
    with pytest.raises(SystemExit, match='1'):
        goss_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'validate' in info['cmd']
    assert '--package' in info['cmd']
    assert 'dpkg' in info['cmd']
    assert '--vars-inline' in info['cmd']
    assert '{"my_service": "httpd", "my_package": "apache"}' in info['cmd']
    assert 'Error: file error: open ./goss.yaml: no such file or directory\n' == info['stdout']
