#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for goss serve"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: goss_serve

short_description: Module to serve a GoSS health endpoint.

version_added: "1.0.0"

description: Serve a GoSS health endpoint for validating systems.

options:
    cache:
        description: Time to cache the results
        required: false
        default: 5s
        type: str
    endpoint:
        description: Endpoint to expose.
        required: false
        default: /healthz
        type: str
    format:
        description: Output format for validation report.
        required: false
        default: rspecish
        type: str
    format_opts:
        description: Extra options passed to the formatter. Valid options are perfdata, pretty, or verbose.
        required: false
        type: str
    gossfile:
        description: The specific gossfile used for serveing the output.
        required: false
        default: goss.yaml
        type: path
    max_concur:
        description: Max number of tests to run concurrently
        required: false
        default: 50
        type: int
    package:
        description: The package type to use.
        required: false
        type: str
    port:
        description: Address to listen on.
        required: false
        default: 8080
        type: int
    vars:
        description: Path to YAML or JSON format file containing variables for template.
        required: false
        type: path
    vars_inline:
        description: Variables for the template.
        required: false
        type: dict

requirements:
    - goss >= 0.4.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# serve a health endpoint with a gossfile at /path/to/my_gossfile.yaml
- name: Serve a health endpoint with a gossfile at /path/to/my_gossfile.yaml
  mschuchard.general.goss_serve:
    gossfile: /path/to/my_gossfile.yaml

# serve a health endpoint with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
- name: Serve a health endpoint with a default location gossfile, a var file at /path/to/vars.yaml, and a pretty json format output
  mschuchard.general.goss_serve:
    format: json
    format_opts: pretty
    vars: /path/to/vars.yaml

# serve a health endpoint with a default location gossfile at localhost:8765/check and cache the results for one minute
- name: Serve a health endpoint with a default location gossfile at localhost:8765/check and cache the results for one minute
  mschuchard.general.goss_serve:
    cache: 1m
    endpoint: /check
    port: 8765

# serve a health endpoint with a default location gossfile and its corresponding golang template with inline variables and rpm package
- name: Serve a health endpoint with a default location gossfile and its corresponding golang template with inline variables and rpm package
  mschuchard.general.goss_serve:
    package: rpm
    vars_inline:
      my_service: httpd
      my_package: apache
"""

RETURN = r"""
command:
    description: The raw GoSS command executed by Ansible.
    type: str
    returned: always
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import goss


def main() -> None:
    """primary function for goss serve module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'cache': {'type': 'str', 'required': False},
            'endpoint': {'type': 'str', 'required': False},
            'format': {'type': 'str', 'required': False},
            'format_opts': {'type': 'str', 'required': False},
            'gossfile': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'max_concur': {'type': 'int', 'required': False},
            'package': {'type': 'str', 'required': False},
            'port': {'type': 'int', 'required': False},
            'vars': {'type': 'path', 'required': False},
            'vars_inline': {'type': 'dict', 'required': False},
        },
        mutually_exclusive=[('vars', 'vars_inline')],
        supports_check_mode=True,
    )

    # initialize
    changed: bool = False
    cache: str = module.params.get('cache')
    endpoint: str = module.params.get('endpoint')
    the_format: str = module.params.get('format')
    format_opts: str = module.params.get('format_opts')
    the_vars: Path = module.params.get('vars')
    vars_inline: dict = module.params.get('vars_inline')
    max_concur: int = module.params.get('max_concur')
    package: str = module.params.get('package')
    port: int = module.params.get('port')
    gossfile: Path = Path(module.params.get('gossfile'))
    cwd: Path = Path.cwd()
    if gossfile != Path.cwd():
        cwd = gossfile.parent

    # check args
    args: dict = {}
    if cache:
        args.update({'cache': cache})
    if endpoint:
        args.update({'endpoint': endpoint})
    if the_format:
        args.update({'format': the_format})
    if format_opts:
        args.update({'format_opts': format_opts})
    if max_concur:
        args.update({'max_concur': max_concur})
    if package:
        args.update({'package': package})
    if port:
        args.update({'port': port})
    if the_vars:
        args.update({'vars': Path(the_vars)})
    elif vars_inline:
        args.update({'vars_inline': vars_inline})

    # determine goss command
    command: list[str] = goss.cmd(action='serve', args=args, gossfile=gossfile)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute goss
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=cwd)

    # check symbolic idempotence
    if len(stdout) > 0:
        changed = True

    # post-process
    if return_code == 0:
        module.exit_json(changed=changed, stdout=stdout, stderr=stderr, command=command)
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
