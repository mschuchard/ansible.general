#!/usr/bin/python
"""ansible module for packer validate"""
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import packer


DOCUMENTATION = r'''
---
module: packer_validate

short_description: Module to manage Packer template and config validation.

version_added: "1.0.0"

description: Checks the template is valid by parsing the template and also checking the configuration with the various builders, provisioners, etc. If it is not valid, the errors will be shown and the module task will exit as a failure.

options:
    config_dir:
        description: Location of the directory or file containing the Packer template(s) and/or config(s).
        required: false
        default: cwd
        type: str
    excepts:
        description: Validate all builds other than these.
        required: false
        default: []
        type: list
    only:
        description: Validate only these builds.
        required: false
        default: []
        type: list
    syntax_only:
        description: Only check syntax. Do not verify config of the template.
        required: false
        default: false
        type: bool
    var:
        description: Variables for templates.
        required: false
        default: []
        type: list
    var_file:
        description: HCL2 files containing user variables.
        required: false
        default: []
        type: list

requirements:
    - packer >= 1.7.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# validate packer templates and configs in /path/to/packer_dir
- name: Validate packer templates and configs in /path/to/packer_dir
  mschuchard.general.packer_validate:
    config_dir: /path/to/packer_dir

# validate only the syntax of the null.this and null.that builds in the packer files
- name: Validate only the null.this and null.that builds in the packer files
  mschuchard.general.packer_validate:
    config_dir: /path/to/packer_dir
    only:
    - null.this
    - null.that
    syntax_only: true

# validate the packer files with vars and var files
- name: Validate the packer files with vars and var files
  mschuchard.general.packer_validate:
    config_dir: /path/to/packer_dir
    var:
    - var_name: var_value
    - var_name_other: var_value_other
    var_file:
    - one.pkrvars.hcl
    - two.pkrvars.hcl
'''

RETURN = r'''
TODO
'''


def run_module() -> None:
    """primary function for packer validate module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec=dict(
            config_dir={'type': 'path', 'required': False, 'default': Path.cwd()},
            excepts={'type': 'list', 'required': False, 'default': []},
            only={'type': 'list', 'required': False, 'default': []},
            syntax_only={'type': 'bool', 'required': False, 'default': False},
            var={'type': 'list', 'required': False, 'default': []},
            var_file={'type': 'list', 'required': False, 'default': []}
        ),
        supports_check_mode=True
    )

    # initialize
    changed: bool = False
    config_dir: Path = Path(module.params.get('config_dir'))
    excepts: list[str] = module.params.get('excepts')
    only: list[str] = module.params.get('only')
    var: list[dict] = module.params.get('var')
    var_file: list[str] = module.params.get('var_file')

    # check optionl params
    flags: list[str] = []
    if module.params.get('syntax_only'):
        flags.append('syntax_only')

    args: dict = {}
    if len(excepts) > 0:
        args.update({'excepts': excepts})
    if len(only) > 0:
        args.update({'only': only})
    if len(var) > 0:
        args.update({'var': var})
    if len(var_file) > 0:
        args.update({'var_file': var_file})

    # convert ansible params to packer args
    args = packer.ansible_to_packer(args)

    # determine packer command
    command: str = packer.cmd(action='validate', flags=flags, args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute packer
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir)

    # post-process
    if return_code == 0:
        module.exit_json(changed=changed, stdout=stdout, stderr=stderr, command=command)
    else:
        module.fail_json(
            msg=stderr.rstrip(), return_code=return_code, cmd=command,
            stdout=stdout, stdout_lines=stdout.splitlines(),
            stderr=stderr, stderr_lines=stderr.splitlines())


def main() -> None:
    """module entrypoint"""
    run_module()


if __name__ == '__main__':
    main()
