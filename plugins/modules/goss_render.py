#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for goss render"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: goss_render

short_description: Module to render a single valid gossfile.

version_added: "1.0.0"

description: Render a single valid parsed JSON/YAML gossfile.

options:
    debug:
        description: Additionally render the golang template prior to rendering the gossfile.
        required: false
        default: false
        type: bool
    gossfile:
        description: The specific gossfile used for rendering the output.
        required: false
        default: goss.yaml
        type: path
    package:
        description: The package type to use.
        required: false
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
# render a gossfile at /path/to/my_gossfile.yaml
- name: Render a gossfile at /path/to/my_gossfile.yaml
  mschuchard.general.goss_render:
    gossfile: /path/to/my_gossfile.yaml

# render a default location gossfile and its corresponding golang template with debug enabled
- name: Render a default location gossfile and its corresponding golang template with debug enabled
  mschuchard.general.goss_render:
    debug: true

# render a default location gossfile and its corresponding golang template with inline variables
- name: Render a default location gossfile and its corresponding golang template with inline variables
  mschuchard.general.goss_render:
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
from mschuchard.general.plugins.module_utils import goss, universal


def main() -> None:
    """primary function for goss render module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'debug': {'type': 'bool', 'required': False},
            'gossfile': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'package': {'type': 'str', 'required': False},
            'vars': {'type': 'path', 'required': False},
            'vars_inline': {'type': 'dict', 'required': False},
        },
        mutually_exclusive=[('vars', 'vars_inline')],
        supports_check_mode=True,
    )

    # initialize
    changed: bool = False
    the_vars: Path = module.params.get('vars')
    vars_inline: dict = module.params.get('vars_inline')
    package: str = module.params.get('package')
    gossfile: Path = Path(module.params.get('gossfile'))
    cwd: Path = Path.cwd() if gossfile == Path.cwd() else gossfile.parent

    # check on optional debug param
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # check args
    args: dict = {}
    if package:
        args.update({'package': package})
    if the_vars:
        args.update({'vars': Path(the_vars)})
    elif vars_inline:
        args.update({'vars_inline': vars_inline})

    # determine goss command
    command: list[str] = goss.cmd(action='render', flags=flags_args[0], args=args, gossfile=gossfile)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute goss
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=cwd)

    # check idempotence
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
