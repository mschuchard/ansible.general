__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import goss_validate
from mschuchard.general.tests.unit.plugins.modules import utils


def test_goss_validate_gossfile(capfd):
    """test goss validate with gossfile"""
    utils.set_module_args({'gossfile': '/tmp'})
    with pytest.raises(SystemExit, match='1'):
        goss_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert 'validate' in info['cmd']
    assert '-g' in info['cmd']
    assert '/tmp' in info['cmd']
    assert 'Error: unknown file extension:' in info['stdout']


def test_goss_validate_format_vars(capfd):
    """test goss validate with format and vars"""
    utils.set_module_args({'format': 'json', 'vars': '/tmp'})
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
    assert '/tmp' in info['cmd']
    assert 'Error: failed while loading vars file "/tmp": Error: loading vars file \'/tmp\'\nread /tmp: is a directory' in info['stdout']
