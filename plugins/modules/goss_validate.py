#!/usr/bin/python
"""ansible module for goss validate"""
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import goss


DOCUMENTATION = r'''
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
    gossfile:
        description: The specific gossfile used for validateing the output.
        required: false
        default: `cwd`/goss.yaml
        type: str
    vars:
        description: Path to YAMl or JSON format file containing variables for template.
        required: false
        type: bool

requirements:
    - goss >= 0.3.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# validate a system with a gossfile at /path/to/my_gossfile.yaml
- name: Validate a system with a gossfile at /path/to/my_gossfile.yaml
  mschuchard.general.goss_validate:
    gossfile: /path/to/my_gossfile.yaml

# validate a system with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
- name: Validate a system with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
  mschuchard.general.goss_validate:
    format: json
    vars: /path/to/vars.yaml
'''

RETURN = r'''
TODO
'''


def main() -> None:
    """primary function for goss validate module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'format': {'type': 'str', 'required': False, 'default': ''},
            'gossfile': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'package': {'type': 'str', 'required': False, 'default': ''},
            'vars': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'vars_inline': {'type': 'dict', 'required': False, 'default': {}}
        },
        mutually_exclusive=[('vars', 'vars_inline')],
        supports_check_mode=True
    )

    # initialize
    changed: bool = False
    the_format: str = module.params.get('format')
    the_vars: Path = Path(module.params.get('vars'))
    vars_inline: dict = module.params.get('vars_inline')
    package: str = module.params.get('package')
    gossfile: Path = Path(module.params.get('gossfile'))
    cwd: str = str(Path.cwd())
    if gossfile != Path.cwd():
        cwd = str(gossfile.parent)

    # check args
    args: dict = {}
    if len(the_format) > 0:
        args.update({'format': the_format})
    if len(package) > 0:
        args.update({'package': package})
    if the_vars != Path.cwd():
        args.update({'vars': str(the_vars)})
    elif len(vars_inline) > 0:
        args.update({'vars_inline': vars_inline})

    # determine goss command
    command: str = goss.cmd(action='validate', args=args, gossfile=gossfile)

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
            msg=stderr.rstrip(), return_code=return_code, cmd=command,
            stdout=stdout, stdout_lines=stdout.splitlines(),
            stderr=stderr, stderr_lines=stderr.splitlines())


if __name__ == '__main__':
    main()
