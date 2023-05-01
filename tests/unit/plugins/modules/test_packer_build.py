"""unit test for packer build module"""
__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import packer_build
from mschuchard.general.tests.unit.plugins.modules import utils


def test_packer_build_defaults(capfd):
    """test packer build with defaults"""
    utils.set_module_args({})
    with pytest.raises(SystemExit, match='1'):
        packer_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'build' in info['cmd']
    assert 'ui,error,Error: Could not find any config file in' in info['stdout']


def test_packer_build_except_onerror_force(capfd):
    """test packer build with only, on_error, and force"""
    utils.set_module_args({
        'config_dir': '/tmp',
        'force': True,
        'on_error': 'abort',
        'only': ['null.this', 'null.that']
    })
    with pytest.raises(SystemExit, match='1'):
        packer_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert '/tmp' in info['cmd']
    assert '-force' in info['cmd']
    assert '-on-error=abort' in info['cmd']
    assert '-only=null.this,null.that' in info['cmd']
    assert 'ui,error,Error: Could not find any config file in /tmp' in info['stdout']


def test_packer_build_except_parallel_timestamp(capfd):
    """test packer build with except, parallel_builds, and timestamp_ui"""
    utils.set_module_args({
        'config_dir': '/tmp',
        'excepts': ['null.this', 'null.that'],
        'parallel_builds': 1,
        'timestamp_ui': True
    })
    with pytest.raises(SystemExit, match='1'):
        packer_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert info['return_code'] == 1
    assert '/tmp' in info['cmd']
    assert '-except=null.this,null.that' in info['cmd']
    assert '-parallel-builds=1' in info['cmd']
    assert '-timestamp-ui' in info['cmd']
    assert 'ui,error,Error: Could not find any config file in /tmp' in info['stdout']


def test_packer_build_var_varfile(capfd):
    """test packer build with var and var_file"""
    utils.set_module_args({
        'var': [{'var_name': 'var_value'}, {'var_name_other': 'var_value_other'}],
        'var_file': ['galaxy.yml', 'galaxy.yml']
    })
    with pytest.raises(SystemExit, match='1'):
        packer_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    print(info)
    assert info['return_code'] == 1
    assert '-var' in info['cmd']
    assert 'var_name=var_value' in info['cmd']
    assert 'var_name_other=var_value_other' in info['cmd']
    assert '-var-file=galaxy.yml' in info['cmd']
    assert '-var-file=galaxy.yml' in info['cmd']
    assert 'ui,error,Error: Could not find any config file in' in info['stdout']
