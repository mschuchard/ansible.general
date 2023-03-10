__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import packer_validate
from mschuchard.general.tests.unit.plugins.modules import utils


def test_packer_validate_defaults(capfd):
    """test packer validate with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='1'):
        packer_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'validate' in info['cmd']
    assert 'ui,error,Error: Could not find any config file in' in info['stdout']


def test_packer_validate_syntax_except(capfd):
    """test packer validate with syntax_only and except"""
    utils.set_module_args({
        'config_dir': '/tmp',
        'excepts': ['null.this', 'null.that'],
        'syntax_only': True
    })
    with pytest.raises(SystemExit, match='1'):
        packer_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert '/tmp' in info['cmd']
    assert '-syntax-only' in info['cmd']
    assert '-except=null.this,null.that' in info['cmd']
    assert 'ui,error,Error: Could not find any config file in /tmp' in info['stdout']


def test_packer_validate_var_varfile(capfd):
    """test packer validate with var and var_file"""
    utils.set_module_args({
        'var': [{'var_name': 'var_value'}, {'var_name_other': 'var_value_other'}],
        'var_file': ['one.pkrvars.hcl', 'two.pkrvars.hcl']
    })
    with pytest.raises(SystemExit, match='1'):
        packer_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    print(info)
    assert info['return_code'] == 1
    assert '-var var_name=var_value' in info['cmd']
    assert '-var var_name_other=var_value_other' in info['cmd']
    assert '-var-file=one.pkrvars.hcl' in info['cmd']
    assert '-var-file=two.pkrvars.hcl' in info['cmd']
    assert 'ui,error,Error: Could not find any config file in' in info['stdout']
