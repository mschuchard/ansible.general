#!/usr/bin/python
"""ansible module for puppet apply"""
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import puppet


DOCUMENTATION = r'''
---
module: puppet apply

short_description: Module to execute a Puppet application of a manifest.

version_added: "1.0.0"

description: The standalone Puppet execution tool used to apply
individual manifests.

options:
    debug:
        description: Enable full debugging.
        required: false
        default: false
        type: bool
    manifest:
        description: The path to the Puppet manifest file to apply.
        required: true
        type: str
    no_op:
        description: Use 'noop' mode where Puppet runs in a no-op or dry-run mode. This is useful for seeing what changes Puppet will make without actually executing the changes.
        required: false
        default: false
        type: bool
    test:
        description: Enable the most common options used for testing. These are 'verbose', 'detailed-exitcodes', and 'show_diff'.
        required: false
        default: false
        type: bool
    verbose:
        description: Print extra information.
        required: false
        default: false
        type: bool

requirements:
    - puppet >= 5.5.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# apply a puppet manifest at manifest.pp with test options
- name: Apply a puppet manifest at manifest.pp with test options
  mschuchard.general.puppet_apply:
    manifest: manifest.pp
    test: true

# apply a puppet manifest at manifest.pp with debug and verbosity enabled in no-operative mode
- name: Apply a puppet manifest at manifest.pp with debug and verbosity enabled in no-operative mode
  mschuchard.general.puppet_apply:
    debug: true
    manifest: manifest.pp
    no_op: true
    verbose: true
'''

RETURN = r'''
command:
    description: The raw Puppet command executed by Ansible.
    type: str
    returned: always
'''


def main() -> None:
    """primary function for puppet apply module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'debug': {'type': 'bool', 'required': False, 'default': False},
            'manifest': {'type': 'path', 'required': True},
            'no_op': {'type': 'bool', 'required': False, 'default': False},
            'test': {'type': 'bool', 'required': False, 'default': False},
            'verbose': {'type': 'bool', 'required': False, 'default': False},
        },
        supports_check_mode=True
    )

    # initialize
    changed: bool = False
    manifest: Path = Path(module.params.get('manifest'))
    test: bool = module.params.get('test')

    # check on optional flag params
    flags: list[str] = []
    if module.params.get('debug'):
        flags.append('debug')
    if module.params.get('no_op'):
        flags.append('no_op')
    if test:
        flags.append('test')
    if module.params.get('verbose'):
        flags.append('verbose')

    # determine puppet command
    command: list[str] = puppet.cmd(action='apply', flags=flags, manifest=manifest)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute puppet
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=str(Path.cwd()))

    # check idempotence
    if test and return_code in [2, 4, 6]:
        changed = True

    # post-process
    if return_code == 0 or changed:
        module.exit_json(changed=changed, stdout=stdout, stderr=stderr, command=command)
    else:
        module.fail_json(
            msg=stderr.rstrip(), return_code=return_code, cmd=command,
            stdout=stdout, stdout_lines=stdout.splitlines(),
            stderr=stderr, stderr_lines=stderr.splitlines())


if __name__ == '__main__':
    main()
