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
        description: Set one or more annotations (ANNOTATION=VALUE)
        required: false
        type: dict
    config_file:
        description: Path to YAML file describing one or more functions
        required: false
        type: path
    constraint:
        description: Apply constraints to the function
        required: false
        type: list
        elements: str
        new_in_version: "1.5.0"
    cpu_limit:
        description: Supply the CPU limit for the function in Mi (when not using a YAML file)
        required: false
        type: str
        new_in_version: "1.5.0"
    cpu_request:
        description: Supply the CPU request for the function in Mi (when not using a YAML file)
        required: false
        type: str
        new_in_version: "1.5.0"
    env:
        description: Set one or more environment variables (ENVVAR=VALUE)
        required: false
        type: dict
        new_in_version: "1.5.0"
    env_subst:
        description: Substitute environment variables in stack.yaml file
        required: false
        default: true
        type: bool
        new_in_version: "1.5.0"
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    fprocess:
        description: fprocess value to be run as a serverless function by the watchdog
        required: false
        type: str
        new_in_version: "1.5.0"
    gateway:
        description: Gateway URL starting with http(s)://
        required: false
        type: str
        new_in_version: "1.5.0"
    handler:
        description: Directory with handler for function (e.g. handler.js)
        required: false
        type: path
        new_in_version: "1.5.0"
    image:
        description: Docker image name to deploy
        required: false
        type: str
        new_in_version: "1.5.0"
    label:
        description: Set one or more labels (LABEL=VALUE)
        required: false
        type: dict
    lang:
        description: Programming language template
        required: false
        type: str
        choices: ['ruby', 'python', 'node', 'csharp']
        new_in_version: "1.5.0"
    memory_limit:
        description: Supply the memory limit for the function in Mi (when not using a YAML file)
        required: false
        type: str
        new_in_version: "1.5.0"
    memory_request:
        description: Supply the memory request for the function in Mi (when not using a YAML file)
        required: false
        type: str
        new_in_version: "1.5.0"
    name:
        description: Name of the deployed function
        required: false
        type: str
    namespace:
        description: Namespace of the function
        required: false
        type: str
        new_in_version: "1.5.0"
    network:
        description: Name of the network
        required: false
        type: str
        new_in_version: "1.5.0"
    read_template:
        description: Read the function's template
        required: false
        default: true
        type: bool
        new_in_version: "1.5.0"
    readonly:
        description: Force the root container filesystem to be read only
        required: false
        default: false
        type: bool
        new_in_version: "1.5.0"
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    replace:
        description: Remove and re-create one or more existing functions
        required: false
        default: false
        type: bool
        removed_in_version: '1.4.0'
    secret:
        description: Give the function access to secure secrets
        required: false
        type: list
        elements: str
        new_in_version: "1.5.0"
    strategy:
        description: Whether to perform rolling update, or remove and re-create, one or more existing functions. This will deprecate the `replace` and `update` parameters in version 1.4.0.
        choices: [replace, update]
        required: false
        default: update
        type: str
        new_in_version: '1.3.1'
    tag:
        description: Override latest tag on function Docker image
        required: false
        default: latest
        type: str
        choices: ['latest', 'sha', 'branch', 'describe']
        new_in_version: "1.5.0"
    timeout:
        description: Timeout for any HTTP calls made to the OpenFaaS API (duration string, e.g. '60s', '1m', '2m30s')
        required: false
        type: str
        new_in_version: "1.5.0"
    tls_no_verify:
        description: Disable TLS validation
        required: false
        default: false
        type: bool
        new_in_version: "1.5.0"
    token:
        description: Pass a JWT token to use instead of basic auth
        required: false
        type: str
        new_in_version: "1.5.0"
    update:
        description: Perform rolling update on one or more existing functions
        required: false
        default: true
        type: bool
        removed_in_version: '1.4.0'

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
- name: Deploy a function from a stack.yaml file with function re-creation, and annotations and labels
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    annotation:
      imageregistry: docker.io
      loadbalancer: mycloud
    label:
      app: myapp
      tier: backend
    strategy: replace

# deploy with environment variables and secrets
- name: Deploy with environment variables and secrets
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    env:
      MYVAR: myval
      DEBUG: "true"
    secret:
    - dockerhuborg
    - api-key

# deploy with resource limits and requests
- name: Deploy with resource limits and requests
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    cpu_limit: 200m
    cpu_request: 100m
    memory_limit: 256Mi
    memory_request: 128Mi

# deploy with tag override
- name: Deploy with SHA tag
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    tag: sha

# deploy directly with image and name
- name: Deploy directly with image and name
  mschuchard.general.faas_deploy:
    image: alexellis/faas-url-ping
    name: url-ping
    gateway: http://remote-site.com:8080

# deploy with constraints and readonly filesystem
- name: Deploy with constraints and readonly filesystem
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    constraint:
    - node.role==worker
    - node.platform.os==linux
    readonly: true

# deploy with custom gateway and TLS settings
- name: Deploy with custom gateway and TLS settings
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    gateway: https://faas.example.com:8080
    tls_no_verify: true
    token: my-jwt-token
    timeout: 2m
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
    """primary function for faas deploy module"""
    # instantiate ansible module
    module: AnsibleModule = AnsibleModule(
        argument_spec={
            'annotation': {'type': 'dict', 'required': False},
            'config_file': {'type': 'path', 'required': False},
            'constraint': {'type': 'list', 'elements': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'cpu_limit': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'cpu_request': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'env': {'type': 'dict', 'required': False, 'new_in_version': '1.5.0'},
            'env_subst': {'type': 'bool', 'required': False, 'default': True, 'new_in_version': '1.5.0'},
            'filter': {'type': 'str', 'required': False},
            'fprocess': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'gateway': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'handler': {'type': 'path', 'required': False, 'new_in_version': '1.5.0'},
            'image': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'label': {'type': 'dict', 'required': False},
            'lang': {'type': 'str', 'required': False, 'choices': ['ruby', 'python', 'node', 'csharp'], 'new_in_version': '1.5.0'},
            'memory_limit': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'memory_request': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'name': {'type': 'str', 'required': False},
            'namespace': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'network': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'read_template': {'type': 'bool', 'required': False, 'default': True, 'new_in_version': '1.5.0'},
            'readonly': {'type': 'bool', 'required': False, 'default': False, 'new_in_version': '1.5.0'},
            'regex': {'type': 'str', 'required': False},
            'replace': {'type': 'bool', 'required': False, 'removed_in_version': '1.4.0'},
            'secret': {'type': 'list', 'elements': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'strategy': {'type': 'str', 'choices': ['replace', 'update'], 'default': 'update', 'required': False, 'new_in_version': '1.3.1'},
            'tag': {'type': 'str', 'required': False, 'default': 'latest', 'choices': ['latest', 'sha', 'branch', 'describe'], 'new_in_version': '1.5.0'},
            'timeout': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'tls_no_verify': {'type': 'bool', 'required': False, 'default': False, 'new_in_version': '1.5.0'},
            'token': {'type': 'str', 'required': False, 'new_in_version': '1.5.0'},
            'update': {'type': 'bool', 'required': False, 'default': True, 'removed_in_version': '1.4.0'},
        },
        mutually_exclusive=[('config_file', 'image'), ('strategy', 'replace'), ('strategy', 'update')],
        required_one_of=[('config_file', 'image')],
        required_together=[('image', 'name')],
        supports_check_mode=True,
    )

    # check on optional strategy param
    flags: set[str] = set()
    if module.params.pop('strategy') == 'replace':
        flags.add('update')
        flags.add('replace')

    # check on optional flags
    if module.params.get('env_subst') is False:
        flags.add('env_subst')
    if module.params.get('read_template') is False:
        flags.add('read_template')
    if module.params.get('readonly'):
        flags.add('readonly')
    if module.params.get('tls_no_verify'):
        flags.add('tls_no_verify')

    # check args
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # convert ansible params to faas args
    faas.ansible_to_faas(flags_args[1])

    # determine faas command
    command: list[str] = faas.cmd(action='deploy', flags=flags, args=flags_args[1])

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
