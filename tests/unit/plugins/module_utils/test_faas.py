"""unit test for faas module util"""

import pytest
from mschuchard.general.plugins.module_utils import faas


def test_faas_cmd_errors():
    """test various cmd errors"""
    # test fails on unsupported action
    with pytest.raises(RuntimeError, match='Unsupported FaaS action attempted: foo'):
        faas.cmd(action='foo')

    # test warns on unknown flag, and discards unknown flag
    with pytest.warns(RuntimeWarning, match='Unsupported flag specified: foo'):
        assert faas.cmd(action='build', flags={'foo'}) == ['faas-cli', 'build']

    # test warns on unknown arg, and discards unknown arg
    with pytest.warns(RuntimeWarning, match='Unsupported FaaS arg specified: foo'):
        assert faas.cmd(action='logs', args={'foo': 'bar'}) == ['faas-cli', 'logs']

    # test warns on specifying args for action without corresponding args, and discards offending arg
    with pytest.warns(RuntimeWarning, match='Unsupported FaaS arg specified: foo'):
        assert faas.cmd(action='remove', args={'foo': 'bar'}) == ['faas-cli', 'remove']

    # test fails on nonexistent function file
    with pytest.raises(FileNotFoundError, match='Function config file does not exist or is invalid: /faas.yaml'):
        faas.cmd(action='build', args={'config_file': '/faas.yaml'})

    # test fails on function file with invalid yaml content
    with pytest.warns(SyntaxWarning, match='Specified YAML or JSON file does not contain valid YAML or JSON: .gitignore'), pytest.raises(ValueError):
        faas.cmd(action='deploy', args={'config_file': '.gitignore'})

    # test fails on soft parameter with invalid value
    with pytest.raises(ValueError, match='The "sort" parameter must be either "name" or "invocations"'):
        faas.cmd(action='list', args={'sort': 'invalid'})


def test_faas_cmd():
    """test various cmd returns"""
    # test list with no flags and no args
    assert faas.cmd(action='list') == ['faas-cli', 'list']

    # test deploy with both flags and no args
    assert set(faas.cmd(action='deploy', flags={'replace', 'update'})) == {'faas-cli', 'deploy', '--replace', '--update=false'}

    # test login with no flags and both args
    assert faas.cmd(action='login', args={'username': 'me', 'password': 'secret'}) == ['faas-cli', 'login', '-u', 'me', '-p', 'secret']

    # test build with pull and quiet and env_subst flags, and name arg
    assert set(faas.cmd(action='build', flags={'pull', 'quiet', 'env_subst'}, args={'name': 'myfunction'})) == {
        'faas-cli',
        'build',
        '--pull',
        '--quiet',
        '--envsubst=false',
        '--name',
        'myfunction',
    }

    # test appends name positional arg for logs action
    assert faas.cmd(action='logs', args={'name': 'myfunction'}) == [
        'faas-cli',
        'logs',
        'myfunction',
    ]

    # test converts parallel arg from int to str for push action
    assert faas.cmd(action='push', args={'parallel': 5}) == [
        'faas-cli',
        'push',
        '--parallel',
        '5',
    ]


def test_ansible_to_faas_errors():
    """test various ansible_to_faas errors"""
    pass


def test_ansible_to_faas():
    """test various ansible_to_faas returns"""
    args: dict = {'label': {'foo': 'bar', 'baz': 'bat'}}
    faas.ansible_to_faas(args=args)
    assert args == {'label': ['--label', 'foo=bar', '--label', 'baz=bat']}
