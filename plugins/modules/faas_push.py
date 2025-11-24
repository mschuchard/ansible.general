#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for faas push"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: faas_push

short_description: Module to push OpenFaaS function container images.

version_added: "1.4.0"

description: Pushes OpenFaaS function container images defined in the supplied YAML config to a remote repository. These container images must already be present in your local image cache.

options:
    config_file:
        description: Path to YAML file describing function(s)
        required: true
        type: path
    env_subst:
        description: Substitute environment variables in stack.yaml file
        required: false
        default: true
        type: bool
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    parallel:
        description: Push images in parallel to depth specified
        required: false
        default: 1
        type: int
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    tag:
        description: Override latest tag on function Docker image
        required: false
        default: latest
        type: str
        choices: ['latest', 'digest', 'sha', 'branch', 'describe']

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# push functions from a stack.yaml file with filter and regex
- name: Push functions from a stack.yaml file with filter and regex
  mschuchard.general.faas_push:
    config_file: stack.yaml
    filter: '*gif*'
    regex: 'fn[0-9]_.*'

# push functions from a stack.yaml file with sha tag, parallel, and without environment substitution
- name: Push functions from a stack.yaml file with sha tag, parallel, and without environment substitution
  mschuchard.general.faas_push:
    config_file: stack.yaml
    parallel: 4
    tag: sha
    env_subst: false
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
    """primary function for faas push module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'config_file': {'type': 'path', 'required': True},
            'env_subst': {'type': 'bool', 'required': False, 'default': True},
            'filter': {'type': 'str', 'required': False},
            'parallel': {'type': 'int', 'required': False},
            'regex': {'type': 'str', 'required': False},
            'tag': {'type': 'str', 'required': False, 'choices': ['latest', 'digest', 'sha', 'branch', 'describe']},
        },
        supports_check_mode=True,
    )

    # check on optional flags
    flags: set[str] = set()
    if module.params.get('env_subst') is False:
        flags.add('env_subst')

    # check args
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # determine faas command
    command: list[str] = faas.cmd(action='push', flags=flags, args=flags_args[1])

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
