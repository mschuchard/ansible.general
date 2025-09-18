#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for goss validate"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: goss_validate

short_description: Module to validate a system with a gossfile.

version_added: "1.0.0"

description: Validate a system with a gossfile or gossfiles.

options:
    format:
        description: Output format for validation report.
        required: false
        default: rspecish
        type: str
        choices: ['documentation', 'json', 'junit', 'nagios', 'prometheus', 'rspecish', 'silent', 'structured', 'tap']
    format_opts:
        description: Extra options passed to the formatter.
        required: false
        type: str
        choices: ['perfdata', 'pretty', 'verbose']
    gossfile:
        description: The specific gossfile used for validating the output.
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
    retry_timeout:
        description: Retry on failure so long as elapsed plus sleep time is less than this.
        required: false
        default: 0s
        type: str
    sleep:
        description: Time to sleep between retries. This parameter only functions when retry_timeout is also set.
        required: false
        default: 1s
        type: str
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
# validate a system with a gossfile at /path/to/my_gossfile.yaml
- name: Validate a system with a gossfile at /path/to/my_gossfile.yaml
  mschuchard.general.goss_validate:
    gossfile: /path/to/my_gossfile.yaml

# validate a system with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
- name: Validate a system with a default location gossfile, a var file at /path/to/vars.yaml, and a pretty json format output
  mschuchard.general.goss_validate:
    format: json
    format_opts: pretty
    vars: /path/to/vars.yaml

# validate a system with retry timeout at fifteen seconds, and a delay between retries at thirty seconds
- name: Validate a system with retry timeout at thirty seconds, and a delay between retries at fifteen seconds
  mschuchard.general.goss_validate:
    retry_timeout: 30s
    sleep: 15s

# validate a system with a default location gossfile and its corresponding golang template with inline variables and dpkg package
- name: Validate a system with a default location gossfile and its corresponding golang template with inline variables and dpkg package
  mschuchard.general.goss_validate:
    package: dpkg
    vars_inline:
      my_service: apache2
      my_package: apache2
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
    """primary function for goss validate module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'format': {
                'type': 'str',
                'required': False,
                'choices': ['documentation', 'json', 'junit', 'nagios', 'prometheus', 'rspecish', 'silent', 'structured', 'tap'],
            },
            'format_opts': {'type': 'str', 'required': False, 'choices': ['perfdata', 'pretty', 'verbose']},
            'gossfile': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'max_concur': {'type': 'int', 'required': False},
            'package': {'type': 'str', 'required': False},
            'retry_timeout': {'type': 'str', 'required': False},
            'sleep': {'type': 'str', 'required': False},
            'vars': {'type': 'path', 'required': False},
            'vars_inline': {'type': 'dict', 'required': False},
        },
        mutually_exclusive=[('vars', 'vars_inline')],
        required_by={'sleep': 'retry_timeout'},
        supports_check_mode=True,
    )

    # initialize
    changed: bool = False
    the_format: str = module.params.get('format')
    format_opts: str = module.params.get('format_opts')
    the_vars: Path = module.params.get('vars')
    vars_inline: dict = module.params.get('vars_inline')
    max_concur: int = module.params.get('max_concur')
    package: str = module.params.get('package')
    retry_timeout: str = module.params.get('retry_timeout')
    sleep: str = module.params.get('sleep')
    gossfile: Path = Path(module.params.get('gossfile'))
    cwd: Path = Path.cwd()
    if gossfile != Path.cwd():
        cwd = gossfile.parent

    # check args
    args: dict = {}
    if the_format:
        args.update({'format': the_format})
    if format_opts:
        args.update({'format_opts': format_opts})
    if max_concur:
        args.update({'max_concur': max_concur})
    if package:
        args.update({'package': package})
    if retry_timeout:
        args.update({'retry_timeout': retry_timeout})
    if sleep:
        args.update({'sleep': sleep})
    if the_vars:
        args.update({'vars': Path(the_vars)})
    elif vars_inline:
        args.update({'vars_inline': vars_inline})

    # determine goss command
    command: list[str] = goss.cmd(action='validate', args=args, gossfile=gossfile)

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
