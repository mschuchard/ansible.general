"""unit test for goss render module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import goss_render
from mschuchard.general.tests.unit.plugins.modules import utils


def test_goss_render_gossfile(capfd):
    """test goss render with gossfile"""
    utils.set_module_args({'gossfile': str(utils.fixtures_dir() / 'goss.yaml')})
    with pytest.raises(SystemExit, match='0'):
        goss_render.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    print(info)
    assert info['changed']
    assert 'size: 4096' in info['stdout']
    assert not info['stderr']
    assert 'render' in info['command']
    assert '-g' in info['command']
    assert str(utils.fixtures_dir() / 'goss.yaml') in info['command']


def test_goss_render_debug(capfd):
    """test goss render with debug"""
    utils.set_module_args({'debug': True, 'gossfile': str(utils.fixtures_dir() / 'goss.yaml')})
    with pytest.raises(SystemExit, match='0'):
        goss_render.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'render' in info['command']
    assert '--debug' in info['command']
    assert 'size: 4096' in info['stdout']


def test_goss_render_vars_inline(capfd):
    """test goss render with inline vars"""
    utils.set_module_args({'vars_inline': {'my_service': 'httpd', 'my_package': 'apache'}, 'gossfile': str(utils.fixtures_dir() / 'goss.yaml')})
    with pytest.raises(SystemExit, match='0'):
        goss_render.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'render' in info['command']
    assert '--vars-inline' in info['command']
    assert '{"my_service": "httpd", "my_package": "apache"}' in info['command']
    assert 'size: 4096' in info['stdout']
