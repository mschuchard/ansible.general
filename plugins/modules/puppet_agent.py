#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for puppet agent"""
__metaclass__ = type

DOCUMENTATION = r'''
---
module: puppet agent

short_description: Module to manage the Puppet agent daemon.

version_added: "1.0.0"

description: Retrieves the client configuration from the Puppet master and applies it to the local host.

options:
    certname:
        description: Set the certname (unique ID) of the client.
        required: false
        default: fqdn
        type: str
    debug:
        description: Enable full debugging.
        required: false
        default: false
        type: bool
    no_daemonize:
        description: Do not send the process into the background.
        required: false
        default: false
        type: bool
    no_op:
        description: Use 'noop' mode where Puppet runs in a no-op or dry-run mode. This is useful for seeing what changes Puppet will make without actually executing the changes.
        required: false
        default: false
        type: bool
    onetime:
        description: Run the configuration once. Runs a single (normally daemonized) Puppet run. Useful for interactively running puppet agent when used in conjunction with the no_daemonize option.
        required: false
        default: false
        type: bool
    server_port:
        description: The port on which to contact the Puppet Server.
        required: false
        default: 8140
        type: int
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
# initiate the puppet agent with test options and server port 8234
- name: Initiate the puppet agent with test options and server port 8234
  mschuchard.general.puppet_agent:
    server_port: 8234
    test: true

# initiate the puppet agent with debug and verbosity enabled in no-operative mode
- name: Initiate the puppet agent with debug and verbosity enabled in no-operative mode
  mschuchard.general.puppet_agent:
    debug: true
    no_op: true
    verbose: true

# initiate the puppet agent once (in a push model)
- name: Initiate the puppet agent once (in a push model)
  mschuchard.general.puppet_agent:
    no_daemonize: true
    onetime: true
'''

RETURN = r'''
command:
    description: The raw Puppet command executed by Ansible.
    type: str
    returned: always
'''

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import puppet


def main() -> None:
    """primary function for puppet agent module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'certname': {'type': 'str', 'required': False},
            'debug': {'type': 'bool', 'required': False, 'default': False},
            'no_daemonize': {'type': 'bool', 'required': False, 'default': False},
            'no_op': {'type': 'bool', 'required': False, 'default': False},
            'onetime': {'type': 'bool', 'required': False, 'default': False},
            'server_port': {'type': 'int', 'required': False},
            'test': {'type': 'bool', 'required': False, 'default': False},
            'verbose': {'type': 'bool', 'required': False, 'default': False},
        },
        supports_check_mode=True
    )

    # initialize
    changed: bool = False
    certname: str = module.params.get('certname')
    server_port: int = module.params.get('server_port')
    test: bool = module.params.get('test')

    # check args
    args: dict = {}
    if certname:
        args.update({'certname': certname})
    if server_port:
        args.update({'server_port': server_port})

    # check on optional flag params
    flags: list[str] = []
    if module.params.get('debug'):
        flags.append('debug')
    if module.params.get('no_daemonize'):
        flags.append('no_daemonize')
    if module.params.get('no_op'):
        flags.append('no_op')
    if module.params.get('onetime'):
        flags.append('onetime')
    if test:
        flags.append('test')
    if module.params.get('verbose'):
        flags.append('verbose')

    # determine puppet command
    command: list[str] = puppet.cmd(action='agent', flags=flags, args=args)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute puppet
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=str(Path.cwd()))

    # check idempotence
    if test and return_code in {2, 4, 6}:
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
