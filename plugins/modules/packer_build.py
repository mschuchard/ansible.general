#!/usr/bin/python
"""ansible module for packer build"""
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import packer


DOCUMENTATION = r'''
---
module: packer_build

short_description: Module to manage Packer template and config artifact builds.

version_added: "1.0.0"

description: Will execute multiple builds in parallel as defined in the template. The various artifacts created by the template will be outputted.

options:
    config_dir:
        description: Location of the directory or file containing the Packer template(s) and/or config(s).
        required: false
        default: cwd
        type: str
    debug:
        description: Debug mode enabled for builds.
        required: false
        default: false
        type: bool
    excepts:
        description: Run all builds and post-processors other than these.
        required: false
        default: []
        type: list
    force:
        description: Force a build to continue if artifacts exist, deletes existing artifacts.
        required: false
        default: false
        type: bool
    on_error:
        description: If the build fails do: clean up (default), abort, ask, or run-cleanup-provisioner
        required: false
        default: ''
        type: str
    only:
        description: Build only the specified builds.
        required: false
        default: []
        type: list
    parallel_builds:
        description: Number of builds to run in parallel. 0 means no limit.
        required: false
        default: 0
        type: int
    timestamp_ui:
        description: Enable prefixing of each ui output with an RFC3339 timestamp.
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
# build packer templates in /path/to/packer_dir
- name: Build packer templates and configs in /path/to/packer_dir
  mschuchard.general.packer_build:
    config_dir: /path/to/packer_dir

# build only the null.this and null.that builds in the packer templates without parallelization and with timestamp display logging
- name: Build only the null.this and null.that builds in the packer templates without parallelization and with timestamp display logging
  mschuchard.general.packer_build:
    config_dir: /path/to/packer_dir
    only:
    - null.this
    - null.that
    parallel_builds: 1
    timestamp_ui: true

# build everything except the null.this and null.that builds in the packer templates without cleanup and remove any existing artifacts
- name: Build everything except the null.this and null.that builds in the packer templates without cleanup and remove any existing artifacts
  mschuchard.general.packer_build:
    config_dir: /path/to/packer_dir
    excepts:
    - null.this
    - null.that
    on_error: abort
    force: true

# build the packer template artifacts with vars and var files
- name: Build the packer template artifacts with vars and var files
  mschuchard.general.packer_build:
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


def main() -> None:
    """primary function for packer build module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'config_dir': {'type': 'path', 'required': False, 'default': Path.cwd()},
            'debug': {'type': 'bool', 'required': False, 'default': False},
            'excepts': {'type': 'list', 'required': False, 'default': []},
            'force': {'type': 'bool', 'required': False, 'default': False},
            'on_error': {'type': 'str', 'required': False, 'default': ''},
            'only': {'type': 'list', 'required': False, 'default': []},
            'parallel_builds': {'type': 'int', 'required': False, 'default': 0},
            'timestamp_ui': {'type': 'bool', 'required': False, 'default': False},
            'var': {'type': 'list', 'required': False, 'default': []},
            'var_file': {'type': 'list', 'required': False, 'default': []}
        },
        supports_check_mode=True
    )

    # initialize
    changed: bool = False
    config_dir: Path = Path(module.params.get('config_dir'))
    excepts: list[str] = module.params.get('excepts')
    on_error: str = module.params.get('on_error')
    only: list[str] = module.params.get('only')
    parallel_builds: int = module.params.get('parallel_builds')
    var: list[dict] = module.params.get('var')
    var_file: list[str] = module.params.get('var_file')

    # check optionl params
    flags: list[str] = []
    if module.params.get('debug'):
        flags.append('debug')
    if module.params.get('force'):
        flags.append('force')
    if module.params.get('timestamp_ui'):
        flags.append('timestamp_ui')

    args: dict = {}
    if len(excepts) > 0:
        args.update({'excepts': excepts})
    if len(on_error) > 0:
        args.update({'on_error': on_error})
    if len(only) > 0:
        args.update({'only': only})
    if parallel_builds > 0:
        args.update({'parallel_builds': parallel_builds})
    if len(var) > 0:
        args.update({'var': var})
    if len(var_file) > 0:
        args.update({'var_file': var_file})

    # convert ansible params to packer args
    args = packer.ansible_to_packer(args)

    # determine packer command
    command: str = packer.cmd(action='build', flags=flags, args=args, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute packer
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir)

    # check idempotence
    if 'artifacts of successful builds' in stdout:
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
