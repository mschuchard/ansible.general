#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for puppet apply"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: puppet_apply

short_description: Module to execute a Puppet application of a manifest.

version_added: "1.0.0"

description: The standalone Puppet execution tool used to apply individual manifests.

options:
    catalog:
        description: Apply a JSON catalog (such as one generated with 'puppet master --compile'). Path to JSON file.
        required: false
        type: path
        new_in_version: "1.4.1"
    debug:
        description: Enable full debugging.
        required: false
        default: false
        type: bool
    detailed_exitcodes:
        description: Provide extra information about the run via exit codes. If enabled, 'puppet apply' will use specific exit codes for different outcomes.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.1"
    execute:
        description: Execute a specific piece of Puppet code.
        required: false
        type: str
        new_in_version: "1.4.1"
    loadclasses:
        description: Load any stored classes. 'puppet agent' caches configured classes (usually at /etc/puppetlabs/puppet/classes.txt), and setting this option causes all of those classes to be set in your puppet manifest.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.1"
    logdest:
        description: Where to send log messages. Choose between 'syslog' (the POSIX syslog service), 'eventlog' (the Windows Event Log), 'console', or the path to a log file. Multiple destinations can be comma-separated.
        required: false
        type: str
        new_in_version: "1.4.1"
    manifest:
        description: The path to the Puppet manifest file to apply.
        required: false
        type: path
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
    write_catalog_summary:
        description: After compiling the catalog saves the resource list and classes list to the node in the state directory named classes.txt and resources.txt.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.1"

requirements:
    - puppet >= 5.5.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
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

# execute inline puppet code
- name: Execute inline puppet code
  mschuchard.general.puppet_apply:
    execute: 'notify { "hello world": }'

# apply a JSON catalog
- name: Apply a JSON catalog
  mschuchard.general.puppet_apply:
    catalog: /path/to/catalog.json

# apply manifest with detailed exit codes and log to file
- name: Apply manifest with detailed exit codes and log to file
  mschuchard.general.puppet_apply:
    manifest: manifest.pp
    detailed_exitcodes: true
    logdest: /var/log/puppet/apply.log

# apply manifest with loadclasses and write catalog summary
- name: Apply manifest with loadclasses and write catalog summary
  mschuchard.general.puppet_apply:
    manifest: manifest.pp
    loadclasses: true
    write_catalog_summary: true
"""

RETURN = r"""
command:
    description: The raw Puppet command executed by Ansible.
    type: str
    returned: always
return_code:
    description: The return code from the Puppet apply execution.
    type: int
    returned: always
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import puppet, universal


def main() -> None:
    """primary function for puppet apply module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'catalog': {'type': 'path', 'required': False, 'new_in_version': '1.4.1'},
            'debug': {'type': 'bool', 'required': False},
            'detailed_exitcodes': {'type': 'bool', 'required': False, 'new_in_version': '1.4.1'},
            'execute': {'type': 'str', 'required': False, 'new_in_version': '1.4.1'},
            'loadclasses': {'type': 'bool', 'required': False, 'new_in_version': '1.4.1'},
            'logdest': {'type': 'str', 'required': False, 'new_in_version': '1.4.1'},
            'manifest': {'type': 'path', 'required': False},
            'no_op': {'type': 'bool', 'required': False},
            'test': {'type': 'bool', 'required': False},
            'verbose': {'type': 'bool', 'required': False},
            'write_catalog_summary': {'type': 'bool', 'required': False, 'new_in_version': '1.4.1'},
        },
        mutually_exclusive=[('manifest', 'execute', 'catalog')],
        required_one_of=[('manifest', 'execute', 'catalog')],
        supports_check_mode=True,
    )

    # initialize
    changed: bool = False
    manifest: Path = Path(module.params.pop('manifest', None))
    catalog: Path = Path(module.params.pop('catalog', None))
    execute: str = module.params.pop('execute', None)
    test: bool = module.params.get('test')

    # check on optional params
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # determine puppet command
    command: list[str] = puppet.cmd(action='apply', flags=flags_args[0], args=flags_args[1], manifest=manifest, catalog=catalog, execute=execute)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute puppet
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=str(Path.cwd()))

    # check idempotence
    if (test or module.params.get('detailed_exitcodes')) and return_code in {2, 4, 6}:
        changed = True

    # post-process
    if return_code == 0 or changed:
        module.exit_json(changed=changed, stdout=stdout, stderr=stderr, return_code=return_code, command=command)
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
