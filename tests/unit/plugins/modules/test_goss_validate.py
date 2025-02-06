"""unit test for goss validate module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import goss_validate
from mschuchard.general.tests.unit.plugins.modules import utils


def test_goss_validate_gossfile(capfd):
    """test goss validate with gossfile"""
    utils.set_module_args({'gossfile': f"{str(utils.fixtures_dir())}/goss.yaml"})
    with pytest.raises(SystemExit, match='1'):
        goss_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'validate' in info['cmd']
    assert '-g' in info['cmd']
    assert str(utils.fixtures_dir() / 'goss.yaml') in info['cmd']
    assert 'File: /etc: size:' in info['stdout']


def test_goss_validate_format_vars(capfd):
    """test goss validate with format and vars"""
    utils.set_module_args({'format': 'json', 'format_opts': 'pretty', 'vars': 'galaxy.yml', 'gossfile': f"{str(utils.fixtures_dir())}/goss.yaml"})
    with pytest.raises(SystemExit, match='1'):
        goss_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'validate' in info['cmd']
    assert '-f' in info['cmd']
    assert 'json' in info['cmd']
    assert '-o' in info['cmd']
    assert 'pretty' in info['cmd']
    assert '--vars' in info['cmd']
    assert 'galaxy.yml' in info['cmd']
    assert 'Error: failed while loading vars file "galaxy.yml"' in info['stdout']


def test_goss_validate_retry_sleep(capfd):
    """test goss validate with retry_timeout and sleep"""
    utils.set_module_args({'retry_timeout': '6s', 'sleep': '3s', 'gossfile': str(utils.fixtures_dir() / 'goss.yaml')})
    with pytest.raises(SystemExit, match='1'):
        goss_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 3
    assert 'validate' in info['cmd']
    assert '-r' in info['cmd']
    assert '6s' in info['cmd']
    assert '-s' in info['cmd']
    assert '3s' in info['cmd']
    assert 'File: /etc: size:' in info['stdout']


def test_goss_validate_package_vars_inline(capfd):
    """test goss validate with package and inline vars"""
    utils.set_module_args({'package': 'dpkg', 'vars_inline': {'my_service': 'httpd', 'my_package': 'apache'}, 'gossfile': f"{str(utils.fixtures_dir())}/goss.yaml"})
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
    assert 'File: /etc: size:' in info['stdout']
