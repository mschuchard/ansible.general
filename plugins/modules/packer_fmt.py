#!/usr/bin/python
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import packer


DOCUMENTATION = r'''
---
module: packer_fmt

short_description: Module to manage Packer template and config canonical formatting.

version_added: "1.0.0"

description: Rewrites all Packer configuration files to a canonical format. Both configuration files (.pkr.hcl) and variable files (.pkrvars.hcl) are updated. JSON files (.json) are not modified. The given content must be in Packer's HCL2 configuration language; JSON is not supported.

options:
    config_dir:
        description: Location of the directory or file containing the Packer template(s) and/or config(s).
        required: false
        default: cwd
        type: str
    check:
        description: Check if the input is formatted. Exit status will be 0 if all input is properly formatted, and non-zero otherwise.
        required: false
        default: false
        type: bool
    recursive:
        description: Also process files in subdirectories. By default only the given directory (or current directory) is processed.
        required: false
        default: false
        type: bool

requirements:
    - packer >= 1.7.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# rewrite Packer files in /path/to/packer_dir to canonical format
- name: Rewrite packer files in /path/to/packer_dir to canonical format
  mschuchard.general.packer_fmt:
    config_dir: /path/to/packer_dir

# verify canonical formatting of Packer files in /path/to/packer_dir
- name: Verify canonical formatting of packer files in /path/to/packer_dir
  mschuchard.general.packer_fmt:
    config_dir: /path/to/packer_dir
    check: true

# recursively rewrite Packer files in current directory to canonical format
- name: Recursively rewrite packer files in current directory to canonical format
  mschuchard.general.packer_fmt:
    recursive: true
'''

RETURN = r'''
TODO
'''


def run_module() -> None:
    """primary function for packer fmt module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec=dict(
            check=dict(type='bool', required=False, default=False),
            config_dir=dict(type='str', required=False, default=Path.cwd()),
            recursive=dict(type='bool', required=False, default=False)
        ),
        supports_check_mode=True
    )

    # initialize
    changed: bool = False
    check: bool = module.params.get('check')
    config_dir: Path = Path(module.params.get('config_dir'))

    # check optionl params
    flags: list[str] = []
    if check:
        flags.append('check')
    if module.params.get('recursive'):
        flags.append('recursive')

    # determine packer command
    command: str = packer.cmd(action='fmt', flags=flags, target_dir=config_dir)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute packer
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=config_dir)

    # check idempotence
    if len(stdout) > 0 and not check:
        changed = True

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
