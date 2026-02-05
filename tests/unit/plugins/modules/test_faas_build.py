"""unit test for faas build module"""

__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import faas_build
from mschuchard.general.tests.unit.plugins.modules import utils


def test_faas_build_defaults(capfd):
    """test faas build with defaults"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml'})
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert 'build' in info['cmd']
    assert '-f' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_build_no_cache_globals(capfd):
    """test faas build with no cache and globals"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'cache': False, 'filter': '*gif*', 'regex': 'fn[0-9]_.*'})
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--no-cache' in info['cmd']
    assert '--filter' in info['cmd']
    assert '*gif*' in info['cmd']
    assert '--regex' in info['cmd']
    assert 'fn[0-9]_.*' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_build_stack_pull_shrinkwrap(capfd):
    """test faas build with disable stack pull, pull, and shrinkwrap"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'stack_pull': False, 'env_subst': False, 'pull': True, 'shrinkwrap': True})
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--disable-stack-pull' in info['cmd']
    assert '--envsubst=false' in info['cmd']
    assert '--pull' in info['cmd']
    assert '--shrinkwrap' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_build_build_arg_build_label(capfd):
    """test faas build with build arguments and build labels"""
    utils.set_module_args(
        {
            'config_file': f'{str(utils.fixtures_dir())}/stack.yaml',
            'build_arg': {'NPM_VERSION': '0.2.2', 'NODE_ENV': 'production'},
            'build_label': {'org.label-schema.version': '1.0.0', 'org.label-schema.name': 'my-function'},
        }
    )
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    print(info)
    assert '--build-arg' in info['cmd']
    assert 'NPM_VERSION=0.2.2' in info['cmd']
    assert 'NODE_ENV=production' in info['cmd']
    assert '--build-label' in info['cmd']
    assert 'org.label-schema.version=1.0.0' in info['cmd']
    assert 'org.label-schema.name=my-function' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_build_build_option_squash(capfd):
    """test faas build with build options and squash"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'build_option': ['dev', 'verbose'], 'squash': True})
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--build-option' in info['cmd']
    assert 'dev' in info['cmd']
    assert 'verbose' in info['cmd']
    assert '--squash' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_build_tag_sha(capfd):
    """test faas build with SHA tag"""
    utils.set_module_args({'config_file': f'{str(utils.fixtures_dir())}/stack.yaml', 'tag': 'sha'})
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--tag' in info['cmd']
    assert 'sha' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_build_direct_params(capfd):
    """test faas build with direct image, handler, lang, and name parameters"""
    utils.set_module_args({'image': 'my_image', 'lang': 'python', 'handler': f'{str(utils.fixtures_dir())}', 'name': 'my_fn', 'squash': True})
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--image' in info['cmd']
    assert 'my_image' in info['cmd']
    assert '--lang' in info['cmd']
    assert 'python' in info['cmd']
    assert '--handler' in info['cmd']
    assert str(utils.fixtures_dir()) in info['cmd']
    assert '--name' in info['cmd']
    assert 'my_fn' in info['cmd']
    assert '--squash' in info['cmd']


def test_faas_build_parallel_copy_extra(capfd):
    """test faas build with parallel depth and copy extra paths"""
    utils.set_module_args(
        {
            'config_file': f'{str(utils.fixtures_dir())}/stack.yaml',
            'parallel': 4,
            'copy_extra': [f'{str(utils.fixtures_dir())}/foo.pkrvars.hcl', f'{str(utils.fixtures_dir())}/goss.yaml'],
        }
    )
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--parallel' in info['cmd']
    assert '4' in info['cmd']
    assert '--copy-extra' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/foo.pkrvars.hcl' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/goss.yaml' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']


def test_faas_build_all_new_params(capfd):
    """test faas build with all new parameters combined"""
    utils.set_module_args(
        {
            'config_file': f'{str(utils.fixtures_dir())}/stack.yaml',
            'build_arg': {'KEY1': 'value1'},
            'build_label': {'label1': 'val1'},
            'build_option': ['dev'],
            'copy_extra': [f'{str(utils.fixtures_dir())}/foo.pkrvars.hcl'],
            'parallel': 2,
            'squash': True,
            'tag': 'branch',
        }
    )
    with pytest.raises(SystemExit, match='1'):
        faas_build.main()

    stdout, stderr = capfd.readouterr()
    assert not stderr

    info = json.loads(stdout)
    assert '--build-arg' in info['cmd']
    assert 'KEY1=value1' in info['cmd']
    assert '--build-label' in info['cmd']
    assert 'label1=val1' in info['cmd']
    assert '--build-option' in info['cmd']
    assert 'dev' in info['cmd']
    assert '--copy-extra' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/foo.pkrvars.hcl' in info['cmd']
    assert '--parallel' in info['cmd']
    assert '2' in info['cmd']
    assert '--squash' in info['cmd']
    assert '--tag' in info['cmd']
    assert 'branch' in info['cmd']
    assert f'{str(utils.fixtures_dir())}/stack.yaml' in info['cmd']
    assert '[\'openfaas\'] is the only valid "provider.name" for the OpenFaaS CLI, but you gave: \n' == info['stdout']
