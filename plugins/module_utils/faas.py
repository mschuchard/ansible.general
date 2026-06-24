"""faas module utilities"""

__metaclass__ = type

import warnings
from typing import Final
from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.mschuchard.general.plugins.module_utils import universal

# dictionary that maps input args to terraform flags
FLAGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'build': {
            'disable_stack_pull': '--disable-stack-pull',
            'env_subst': '--envsubst=false',
            'no_cache': '--no-cache',
            'pull': '--pull',
            'quiet': '--quiet',
            'shrinkwrap': '--shrinkwrap',
            'squash': '--squash',
        },
        'deploy': {
            'env_subst': '--envsubst=false',
            'read_template': '--read-template=false',
            'readonly': '--readonly',
            'replace': '--replace',
            'tls_no_verify': '--tls-no-verify',
            'update': '--update=false',
        },
        'list': {
            'env_subst': '--envsubst=false',
            'quiet': '-q',
            'tls_no_verify': '--tls-no-verify',
            'verbose': '-v',
        },
        'login': {
            'password_stdin': '-s',
            'tls_no_verify': '--tls-no-verify',
        },
        'logs': {
            'instance': '--instance',
            'print_name': '--name',
            'tail': '--tail=false',
            'tls_no_verify': '--tls-no-verify',
        },
        'push': {
            'env_subst': '--envsubst=false',
            'quiet': '--quiet',
        },
        'remove': {
            'env_subst': '--envsubst=false',
            'tls_no_verify': '--tls-no-verify',
        },
    }
)

# dictionary that maps input args to terraform args
ARGS_MAP: Final[dict[str, dict[str, str]]] = dict(
    {
        'build': {
            'build_arg': '',
            'build_label': '',
            'build_option': '',
            'copy_extra': '',
            'handler': '--handler',
            'image': '--image',
            'lang': '--lang',
            'name': '--name',
            'parallel': '--parallel',
            'tag': '--tag',
        },
        'deploy': {
            'annotation': '',
            'constraint': '',
            'cpu_limit': '--cpu-limit',
            'cpu_request': '--cpu-request',
            'env': '',
            'fprocess': '--fprocess',
            'gateway': '--gateway',
            'handler': '--handler',
            'image': '--image',
            'label': '',
            'lang': '--lang',
            'memory_limit': '--memory-limit',
            'memory_request': '--memory-request',
            'name': '--name',
            'namespace': '--namespace',
            'network': '--network',
            'secret': '',
            'tag': '--tag',
            'timeout': '--timeout',
            'token': '--token',
        },
        'list': {
            'gateway': '--gateway',
            'namespace': '--namespace',
            'sort': '--sort',
            'token': '--token',
        },
        'logs': {
            'gateway': '-g',
            'lines': '--lines',
            'name': '',
            'namespace': '-n',
            'output': '-o',
            'since': '--since',
            'since_time': '--since-time',
            'time_format': '--time-format',
            'token': '-k',
        },
        'login': {
            'gateway': '-g',
            'password': '-p',
            'timeout': '--timeout',
            'username': '-u',
        },
        'push': {
            'parallel': '--parallel',
            'tag': '--tag',
        },
        'remove': {
            'gateway': '-g',
            'name': '',
            'namespace': '-n',
            'token': '-k',
        },
    }
)


def cmd(action: str, flags: set[str] = set(), args: dict[str, str | int | list[str]] = {}) -> list[str]:
    """constructs a list representing the openfaas command to execute"""
    # verify command
    if action not in FLAGS_MAP | ARGS_MAP:
        raise RuntimeError(f'Unsupported FaaS action attempted: {action}')

    # initialize faas-cli command
    command: list[str] = ['faas-cli', action] + global_args_to_cmd(args=args)

    # append list of flag commands
    universal.action_flags_command(command, flags, FLAGS_MAP.get(action, {}))

    # construct list of faas args
    # not all actions have args, so return empty dict by default to shortcut to RuntimeError for unsupported arg if arg specified for action without args
    action_args_map: dict[str, str] = ARGS_MAP.get(action, {})
    positional_arg: str | None = None
    for arg, arg_value in args.items():
        # verify this is a valid action argument
        if arg in action_args_map:
            if arg == 'sort' and arg_value not in ['name', 'invocations']:
                raise ValueError('The "sort" parameter must be either "name" or "invocations"')
            # annotation, label, build_arg, build_label, build_option, copy_extra, constraint, env, and secret have properly formatted value of type list[str] and so need to be extended directly
            if arg in ['annotation', 'label', 'build_arg', 'build_label', 'build_option', 'copy_extra', 'constraint', 'env', 'secret'] and isinstance(
                arg_value, list
            ):
                command.extend(arg_value)
            # name arg is actually positional for logs and remove; defer until after all other args
            elif action in ['logs', 'remove'] and arg == 'name':
                positional_arg = str(arg_value)
            # append the value interpolated with the arg name from the dict to the command (iterable)
            elif isinstance(arg_value, list):
                command.extend([action_args_map[arg]] + arg_value)
            # append the value interpolated with the arg name from the dict to the command (non-iterable)
            elif isinstance(arg_value, (str, int)):
                command.extend([action_args_map[arg], str(arg_value)])
            # an invalid arg value and type combination was specified
            else:
                raise ValueError(f'The specified parameter value and type for {arg} is not acceptable for the FaaS module plugin')
        else:
            # unsupported arg specified
            warnings.warn(f'Unsupported FaaS arg specified: {arg}', RuntimeWarning)

    # append positional arg last so it is always the final element of the command
    if positional_arg is not None:
        command.append(positional_arg)

    return command


def global_args_to_cmd(args: dict = {}) -> list[str]:
    """converts openfaas global arguments into a list of strings suitable for extending to a command"""
    # initialize command to return
    command: list[str] = []

    # check if filter is specified
    if 'filter' in args:
        command.extend(['--filter', args['filter']])
        del args['filter']

    # check if regex is specified
    if 'regex' in args:
        command.extend(['--regex', args['regex']])
        del args['regex']

    # check if config file is specified
    if 'config_file' in args:
        config_file: Path = Path(args['config_file'])
        # verify faas function config file is a file, and a valid yaml file
        if config_file.is_file() and universal.validate_json_yaml_file(config_file):
            # config file is valid
            command.extend(['-f', str(config_file)])
            del args['config_file']
        else:
            # error if config file has issue
            raise FileNotFoundError(f'Function config file does not exist or is invalid: {config_file}')

    return command


def ansible_to_faas(args: dict) -> None:
    """converts ansible types and syntax to faas types and formatting for arguments only"""
    # in this function args dict is mutable pseudo-reference and also returned
    # iterate through ansible module argument
    for arg, arg_value in args.items():
        match arg:
            # transform dict[str, str] to list of '--arg' 'key=value' '--arg' 'key2=value2' strings
            case 'annotation' | 'label' | 'build_arg' | 'build_label' | 'env':
                args[arg] = ' '.join([f'--{arg.replace("_", "-")} {key}={value}' for key, value in arg_value.items()]).split()
            # transform list[str] to list of '--build-option' 'value1' '--build-option' 'value2' strings
            case 'build_option':
                args[arg] = ' '.join([f'--build-option {value}' for value in arg_value]).split()
            # transform list[Path] to list of '--copy-extra' 'path1' '--copy-extra' 'path2' strings
            case 'copy_extra':
                args[arg] = ' '.join([f'--copy-extra {str(path)}' for path in arg_value]).split()
            # transform list[str] to list of '--constraint' 'value1' '--constraint' 'value2' strings
            case 'constraint':
                args[arg] = ' '.join([f'--constraint {value}' for value in arg_value]).split()
            # transform list[str] to list of '--secret' 'value1' '--secret' 'value2' strings
            case 'secret':
                args[arg] = ' '.join([f'--secret {value}' for value in arg_value]).split()


def is_deployed(module: AnsibleModule, flags: set[str], args: dict) -> bool | None:
    """determine if one or more faas functions are currently deployed
    returns True if all functions are deployed, False if none are, and None if partial deployment detected
    flags and args should already be resolved from the calling module params"""
    # construct list command reusing existing flag and arg resolution from module plugin
    list_command: list[str] = cmd(action='list', flags=flags, args=args.copy())

    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(list_command)

    # list command failure, warn, and permit the caller to proceed and surface the real error
    if return_code != 0:
        module.warn(f'faas-cli list failed during deployment check; proceeding: {stderr.rstrip()}')
        # safer to assume function not deployed than is deployed
        return False

    # determine if list returned deployed functions based on stdout
    return len(stdout.splitlines()) > 1
