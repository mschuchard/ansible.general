"""unit test for packer validate module"""
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


def test_packer_validate_eval_datasource_warn_undeclared(capfd):
    """test packer validate with evaluate datasources and do not warn undeclared vars"""
    utils.set_module_args({
        'evaluate_datasources': True,
        'warn_undeclared_var': False,
        'config_dir': str(utils.fixtures_dir())
    })
    with pytest.raises(SystemExit, match='1'):
        packer_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '-evaluate-datasources' in info['cmd']
    assert '-no-warn-undeclared-var' in info['cmd']
    assert str(utils.fixtures_dir()) == info['cmd'][-1]
    assert 'No instructions given for handling the artifact' in info['stdout']


def test_packer_validate_syntax_except(capfd):
    """test packer validate with syntax_only and except"""
    utils.set_module_args({
        'config_dir': str(utils.fixtures_dir()),
        'excepts': ['null.this', 'null.that'],
        'syntax_only': True
    })
    with pytest.raises(SystemExit, match='0'):
        packer_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert not info['changed']
    assert str(utils.fixtures_dir()) == info['command'][-1]
    assert '-syntax-only' in info['command']
    assert '-except=null.this,null.that' in info['command']
    assert 'ui,say,Syntax-only check passed. Everything looks okay.' in info['stdout']


def test_packer_validate_var_varfile(capfd):
    """test packer validate with var and var_file"""
    utils.set_module_args({
        'var': [{'var_name': 'var_value'}, {'var_name_other': 'var_value_other'}],
        'var_file': [f"{str(utils.fixtures_dir())}/foo.pkrvars.hcl", f"{str(utils.fixtures_dir())}/foo.pkrvars.hcl"],
        'config_dir': str(utils.fixtures_dir())
    })
    with pytest.raises(SystemExit, match='1'):
        packer_validate.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '-var' in info['cmd']
    assert 'var_name=var_value' in info['cmd']
    assert 'var_name_other=var_value_other' in info['cmd']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.pkrvars.hcl" in info['cmd']
    assert f"-var-file={str(utils.fixtures_dir())}/foo.pkrvars.hcl" in info['cmd']
    assert 'ui,error,Warning: Undefined variable' in info['stdout']
    assert str(utils.fixtures_dir()) == info['cmd'][-1]
