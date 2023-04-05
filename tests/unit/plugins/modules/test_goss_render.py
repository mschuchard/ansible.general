__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import goss_render
from mschuchard.general.tests.unit.plugins.modules import utils


def test_goss_render_gossfile(capfd):
    """test goss render with gossfile"""
    utils.set_module_args({'gossfile': '/tmp'})
    with pytest.raises(SystemExit, match='1'):
        goss_render.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'render' in info['cmd']
    assert '-g' in info['cmd']
    assert '/tmp' in info['cmd']
    assert 'unknown file extension:' in info['stderr']


def test_goss_render_debug(capfd):
    """test goss render with debug"""
    utils.set_module_args({'debug': True})
    with pytest.raises(SystemExit, match='1'):
        goss_render.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'render' in info['cmd']
    assert '-g' not in info['cmd']
    assert '--debug' in info['cmd']
    assert 'file error: open ./goss.yaml: no such file or directory' in info['stderr']
