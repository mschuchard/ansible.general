#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for faas build"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: faas_build

short_description: Module to build a FaaS function container.

version_added: "1.0.0"

description: Builds OpenFaaS function containers either via the supplied YAML config, or via parameters.

options:
    config_file:
        description: Path to YAML file describing function(s)
        required: false
        type: path
    disable_stack_pull:
        description: Disables the template configuration in the stack.yaml
        required: false
        default: false
        type: bool
    env_subst:
        description: Substitute environment variables in stack.yaml file
        required: false
        default: true
        type: bool
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    name:
        description: Name of the deployed function
        required: false
        type: str
    no_cache:
        description: Do not use Docker's build cache
        required: false
        default: false
        type: bool
    pull:
        description: Force a re-pull of base images in template during build, useful for publishing images
        required: false
        default: false
        type: bool
    quiet:
        description: Perform a quiet build, without showing output from Docker
        required: false
        default: false
        type: bool
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    shrinkwrap:
        description: Just write files to ./build/ folder for shrink-wrapping
        required: false
        default: false
        type: bool

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# build a function from a stack.yaml file with no cache, filter, and regex
- name: Build a function from a stack.yaml file with no cache, filter, and regex
  mschuchard.general.faas_build:
    config_file: stack.yaml
    no_cache: True
    filter: '*gif*'
    regex: 'fn[0-9]_.*'

# build a function from a stack.yaml file with pull, shrinkwrap, and disabled stack pull
- name: Build a function from a stack.yaml file with pull, shrinkwrap, and disabled stack pull
  mschuchard.general.faas_build:
    config_file: stack.yaml
    disable_stack_pull: True
    pull: True
    shrinkwrap: True
"""

RETURN = r"""
command:
    description: The raw FaaS CLI command executed by Ansible.
    type: str
    returned: always
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import faas


def main() -> None:
    """primary function for faas build module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'config_file': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'disable_stack_pull': {'type': 'bool', 'default': False},
            'env_subst': {'type': 'bool', 'default': True},
            'filter': {'type': 'str', 'required': False},
            'name': {'type': 'str', 'required': False},
            'no_cache': {'type': 'bool', 'default': False},
            'pull': {'type': 'bool', 'default': False},
            'quiet': {'type': 'bool', 'default': False},
            'regex': {'type': 'str', 'required': False},
            'shrinkwrap': {'type': 'bool', 'default': False},
        },
        mutually_exclusive=[('config_file', 'name')],
        required_one_of=[('config_file', 'name')],
        supports_check_mode=True,
    )

    # initialize
    filter: str = module.params.get('filter')
    name: str = module.params.get('name')
    regex: str = module.params.get('regex')
    config_file: Path = module.params.get('config_file')

    # check on optional debug param
    flags: set[str] = set()
    if module.params.get('disable_stack_pull'):
        flags.add('disable_stack_pull')
    if module.params.get('env_subst'):
        flags.add('envsubst')
    if module.params.get('no_cache'):
        flags.add('no_cache')
    if module.params.get('pull'):
        flags.add('pull')
    if module.params.get('quiet'):
        flags.add('quiet')
    if module.params.get('shrinkwrap'):
        flags.add('shrinkwrap')

    # check args
    args: dict = {}
    if filter:
        args.update({'filter': filter})
    if name:
        args.update({'name': name})
    if regex:
        args.update({'regex': regex})
    elif config_file:
        args.update({'config_file': Path(config_file)})

    # determine faas command
    command: list[str] = faas.cmd(action='build', flags=flags, args=args)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute faas
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=str(Path.cwd()))

    # post-process
    if return_code == 0:
        module.exit_json(changed=True, stdout=stdout, stderr=stderr, command=command)
    else:
        module.fail_json(
            msg=stderr.rstrip(),
            return_code=return_code,
            cmd=command,
            stdout=stdout,
            stdout_lines=stdout.splitlines(),
            stderr=stderr,
            stderr_lines=stderr.splitlines(),
        )


if __name__ == '__main__':
    main()
