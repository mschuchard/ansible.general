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

version_added: "1.3.0"

description: Builds OpenFaaS function containers either via the supplied YAML config, or via parameters.

options:
    build_arg:
        description: Add build arguments for Docker (KEY=VALUE pairs)
        required: false
        type: dict
        new_in_version: "1.5.0"
    build_label:
        description: Add labels for Docker image (LABEL=VALUE pairs)
        required: false
        type: dict
        new_in_version: "1.5.0"
    build_option:
        description: Set build options (e.g. dev)
        required: false
        type: list
        elements: str
        new_in_version: "1.5.0"
    cache:
        description: Use Docker's build cache
        required: false
        default: true
        type: bool
    config_file:
        description: Path to YAML file describing function(s)
        required: false
        type: path
    copy_extra:
        description: Extra paths that will be copied into the function build context
        required: false
        type: list
        elements: path
        new_in_version: "1.5.0"
    env_subst:
        description: Substitute environment variables in stack.yaml file
        required: false
        default: true
        type: bool
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    handler:
        description: Directory with handler for function (e.g. handler.js)
        required: false
        type: path
        new_in_version: "1.5.0"
    image:
        description: Docker image name to build
        required: false
        type: str
        new_in_version: "1.5.0"
    lang:
        description: Programming language template
        required: false
        type: str
        choices: ['ruby', 'python', 'python3', 'node', 'csharp', 'dockerfile']
        new_in_version: "1.5.0"
    name:
        description: Name of the deployed function
        required: false
        type: str
    parallel:
        description: Build in parallel to depth specified
        required: false
        default: 1
        type: int
        new_in_version: "1.5.0"
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
    squash:
        description: Use Docker's squash flag for smaller images [experimental]
        required: false
        default: false
        type: bool
        new_in_version: "1.5.0"
    stack_pull:
        description: Enables the template configuration in the stack.yaml
        required: false
        default: true
        type: bool
    tag:
        description: Override latest tag on function Docker image
        required: false
        default: latest
        type: str
        choices: ['latest', 'digest', 'sha', 'branch', 'describe']
        new_in_version: "1.5.0"

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# build a function from a stack.yaml file with no cache, filter, and regex
- name: Build a function from a stack.yaml file with no cache, filter, and regex
  mschuchard.general.faas_build:
    config_file: stack.yaml
    cache: false
    filter: '*gif*'
    regex: 'fn[0-9]_.*'

# build a function from a stack.yaml file with pull and shrinkwrap, and disabled stack pull and environment substitution
- name: Build a function from a stack.yaml file with pull and shrinkwrap, and disabled stack pull and environment substitution
  mschuchard.general.faas_build:
    config_file: stack.yaml
    stack_pull: false
    env_subst: false
    pull: true
    shrinkwrap: true

# build with build arguments and build labels
- name: Build with build arguments and build labels
  mschuchard.general.faas_build:
    config_file: stack.yaml
    build_arg:
      NPM_VERSION: 0.2.2
      NODE_ENV: production
    build_label:
      org.label-schema.version: 1.0.0
      org.label-schema.name: my-function

# build with build options and squash
- name: Build with build options and squash
  mschuchard.general.faas_build:
    config_file: stack.yaml
    build_option:
    - dev
    - verbose
    squash: true

# build with tag override
- name: Build with SHA tag
  mschuchard.general.faas_build:
    config_file: stack.yaml
    tag: sha

# build directly with image, handler, and language
- name: Build directly with image, handler, and language
  mschuchard.general.faas_build:
    image: my_image
    lang: python
    handler: /path/to/fn/
    name: my_fn
    squash: true

# build with parallel depth and copy extra paths
- name: Build with parallel depth and copy extra paths
  mschuchard.general.faas_build:
    config_file: stack.yaml
    parallel: 4
    copy_extra:
    - /path/to/extra/files
    - /another/path
"""

RETURN = r"""
command:
    description: The raw FaaS CLI command executed by Ansible.
    type: str
    returned: always
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import faas, universal


def main() -> None:
    """primary function for faas build module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'build_arg': {'type': 'dict', 'required': False, 'new_in_version': '1.5.0'},
            'build_label': {'type': 'dict', 'required': False, 'new_in_version': '1.5.0'},
            'build_option': {'type': 'list', 'elements': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'cache': {'type': 'bool', 'required': False, 'default': True},
            'config_file': {'type': 'path', 'required': False},
            'copy_extra': {'type': 'list', 'elements': 'path', 'required': False, 'new_in_version': '1.5.0'},
            'env_subst': {'type': 'bool', 'required': False, 'default': True},
            'filter': {'type': 'str', 'required': False},
            'handler': {'type': 'path', 'required': False, 'new_in_version': '1.5.0'},
            'image': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'lang': {'type': 'str', 'required': False, 'choices': ['ruby', 'python', 'python3', 'node', 'csharp', 'dockerfile'], 'new_in_version': '1.5.0'},
            'name': {'type': 'str', 'required': False},
            'parallel': {'type': 'int', 'required': False, 'default': 1, 'new_in_version': '1.5.0'},
            'pull': {'type': 'bool', 'required': False},
            'quiet': {'type': 'bool', 'required': False},
            'regex': {'type': 'str', 'required': False},
            'shrinkwrap': {'type': 'bool', 'required': False},
            'squash': {'type': 'bool', 'required': False, 'new_in_version': '1.5.0'},
            'stack_pull': {'type': 'bool', 'required': False, 'default': True},
            'tag': {
                'type': 'str',
                'required': False,
                'default': 'latest',
                'choices': ['latest', 'digest', 'sha', 'branch', 'describe'],
                'new_in_version': '1.5.0',
            },
        },
        mutually_exclusive=[('config_file', 'image'), ('config_file', 'handler'), ('config_file', 'lang')],
        required_one_of=[('config_file', 'image')],
        required_together=[('image', 'handler', 'name')],
        supports_check_mode=True,
    )

    # check on optional debug param
    flags: set[str] = set()
    if module.params.get('stack_pull') is False:
        flags.add('disable_stack_pull')
    if module.params.get('env_subst') is False:
        flags.add('env_subst')
    if module.params.get('cache') is False:
        flags.add('no_cache')
    if module.params.get('pull'):
        flags.add('pull')
    if module.params.get('quiet'):
        flags.add('quiet')
    if module.params.get('shrinkwrap'):
        flags.add('shrinkwrap')
    if module.params.get('squash'):
        flags.add('squash')

    # check args
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # convert ansible params to faas args
    faas.ansible_to_faas(flags_args[1])

    # determine faas command
    command: list[str] = faas.cmd(action='build', flags=flags, args=flags_args[1])

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
