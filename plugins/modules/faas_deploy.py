#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for faas deploy"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: faas_deploy

short_description: Module to deploy OpenFaaS function containers.

version_added: "1.3.0"

description: Deploys OpenFaaS function containers either via the supplied YAML config, or via parameters.

options:
    annotation:
        description: Set one or more annotations
        required: false
        type: dict
    config_file:
        description: Path to YAML file describing one or more functions
        required: false
        type: path
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    label:
        description: Set one or more labels
        required: false
        type: dict
    name:
        description: Name of the deployed function
        required: false
        type: str
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    replace:
        description: Remove and re-create one or more existing functions
        required: false
        default: false
        type: bool
    update:
        description: Perform rolling update on one or more existing functions
        required: false
        default: true
        type: bool

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# deploy a function from a stack.yaml file with function re-creation and no rolling updates, filter, and regex
- name: Deploy a function from a stack.yaml file with function re-creation and no rolling updates, filter, and regex
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    replace: true
    update: false
    filter: '*gif*'
    regex: 'fn[0-9]_.*'

# deploy a function from a stack.yaml file with annotations and labels
- name: Deploy a function from a stack.yaml file with annotations and labels
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    annotation:
      imageregistry: docker.io
      loadbalancer: mycloud
    label:
      app: myapp
      tier: backend
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
    """primary function for faas deploy module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'annotation': {'type': 'dict', 'required': False},
            'config_file': {'type': 'path', 'required': False},
            'filter': {'type': 'str', 'required': False},
            'label': {'type': 'dict', 'required': False},
            'name': {'type': 'str', 'required': False},
            'regex': {'type': 'str', 'required': False},
            'replace': {'type': 'bool', 'required': False},
            'update': {'type': 'bool', 'required': False, 'default': True},
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
    annotation: dict = module.params.get('annotation')
    label: dict = module.params.get('label')

    # check on optional debug param
    flags: set[str] = set()
    if module.params.get('update') is False:
        flags.add('update')
    if module.params.get('replace'):
        flags.add('replace')

    # check args
    args: dict = {}
    if filter:
        args.update({'filter': filter})
    if name:
        args.update({'name': name})
    elif config_file:
        args.update({'config_file': Path(config_file)})
    if regex:
        args.update({'regex': regex})
    if annotation:
        args.update({'annotation': annotation})
    if label:
        args.update({'label': label})

    # convert ansible params to faas args
    args = faas.ansible_to_faas(args)

    # determine faas command
    command: list[str] = faas.cmd(action='deploy', flags=flags, args=args)

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
