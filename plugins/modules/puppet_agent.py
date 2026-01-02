#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for puppet agent"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: puppet_agent

short_description: Module to manage the Puppet agent daemon.

version_added: "1.0.0"

description: Retrieves the client configuration from the Puppet master and applies it to the local host.

options:
    certname:
        description: Set the certname (unique ID) of the client.
        required: false
        default: client's FQDN
        type: str
    debug:
        description: Enable full debugging.
        required: false
        default: false
        type: bool
    digest:
        description: Change the certificate fingerprinting digest algorithm. Only used with fingerprint parameter.
        required: false
        default: SHA256
        type: str
        choices: ['MD5', 'SHA1', 'SHA256']
        new_in_version: "1.4.1"
    disable:
        description: Disable working on the local system with optional lock message. Puppet agent exits after executing this.
        required: false
        type: str
        new_in_version: "1.4.1"
    enable:
        description: Enable working on the local system by removing lock file. Puppet agent exits after executing this.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.1"
    evaltrace:
        description: Logs each resource as it is being evaluated for interactive debugging.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.1"
    fingerprint:
        description: Display current certificate or certificate signing request fingerprint and exit.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.1"
    job_id:
        description: Attach specified job id to catalog request and report. Only works with onetime parameter. Do not use with Puppet Enterprise Orchestrator.
        required: false
        type: str
        new_in_version: "1.4.1"
    logdest:
        description: Where to send log messages. Can be 'syslog', 'eventlog', 'console', or path to log file. Multiple destinations can be comma-separated.
        required: false
        type: str
        new_in_version: "1.4.1"
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
    sourceaddress:
        description: Set the source IP address for transactions.
        required: false
        type: str
        new_in_version: "1.4.1"
    test:
        description: Enable the most common options used for testing. These are 'verbose', 'detailed-exitcodes', and 'show_diff'.
        required: false
        default: false
        type: bool
    trace:
        description: Print stack traces on errors.
        required: false
        default: false
        type: bool
        new_in_version: "1.4.1"
    verbose:
        description: Print extra information.
        required: false
        default: false
        type: bool
    waitforcert:
        description: Connect to server every N seconds to request certificate signing. Set to 0 to disable. Only matters for agents without certificates.
        required: false
        default: 120
        type: int
        new_in_version: "1.4.1"

requirements:
    - puppet >= 5.5.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
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

# run puppet agent with specific source IP and log to file
- name: Run puppet agent with specific source IP and log to file
  mschuchard.general.puppet_agent:
    sourceaddress: 192.168.1.100
    logdest: /var/log/puppet/agent.log
    onetime: true

# display certificate fingerprint using SHA1 digest
- name: Display certificate fingerprint using SHA1 digest
  mschuchard.general.puppet_agent:
    fingerprint: true
    digest: SHA1

# run puppet agent once with job ID for orchestration
- name: Run puppet agent once with job ID for orchestration
  mschuchard.general.puppet_agent:
    onetime: true
    job_id: ansible-run-12345

# disable puppet agent with message
- name: Disable puppet agent with maintenance message
  mschuchard.general.puppet_agent:
    disable: "System maintenance in progress"

# enable puppet agent
- name: Enable puppet agent
  mschuchard.general.puppet_agent:
    enable: true

# run with resource evaluation tracing and stack traces
- name: Run with detailed debugging
  mschuchard.general.puppet_agent:
    evaltrace: true
    trace: true
    onetime: true
"""

RETURN = r"""
command:
    description: The raw Puppet command executed by Ansible.
    type: str
    returned: always
return_code:
    description: The return code from the Puppet agent execution.
    type: int
    returned: always
"""

from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import puppet, universal


def main() -> None:
    """primary function for puppet agent module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec={
            'certname': {'type': 'str', 'required': False},
            'debug': {'type': 'bool', 'required': False},
            'digest': {'type': 'str', 'required': False, 'default': 'SHA256', 'choices': ['MD5', 'SHA1', 'SHA256'], 'new_in_version': '1.4.1'},
            'disable': {'type': 'str', 'required': False, 'new_in_version': '1.4.1'},
            'enable': {'type': 'bool', 'required': False, 'new_in_version': '1.4.1'},
            'evaltrace': {'type': 'bool', 'required': False, 'new_in_version': '1.4.1'},
            'fingerprint': {'type': 'bool', 'required': False, 'new_in_version': '1.4.1'},
            'job_id': {'type': 'str', 'required': False, 'new_in_version': '1.4.1'},
            'logdest': {'type': 'str', 'required': False, 'new_in_version': '1.4.1'},
            'no_daemonize': {'type': 'bool', 'required': False},
            'no_op': {'type': 'bool', 'required': False},
            'onetime': {'type': 'bool', 'required': False},
            'server_port': {'type': 'int', 'required': False},
            'sourceaddress': {'type': 'str', 'required': False, 'new_in_version': '1.4.1'},
            'test': {'type': 'bool', 'required': False},
            'trace': {'type': 'bool', 'required': False, 'new_in_version': '1.4.1'},
            'verbose': {'type': 'bool', 'required': False},
            'waitforcert': {'type': 'int', 'required': False, 'new_in_version': '1.4.1'},
        },
        mutually_exclusive=[('disable', 'enable'), ('disable', 'test'), ('disable', 'onetime'), ('enable', 'test'), ('enable', 'onetime')],
        required_by={'job_id': ['onetime'], 'digest': ['fingerprint']},
        supports_check_mode=True,
    )

    # initialize
    changed: bool = False

    # check optional params
    flags_args: tuple[set[str], dict] = universal.params_to_flags_args(module.params, module.argument_spec)

    # determine puppet command
    command: list[str] = puppet.cmd(action='agent', flags=flags_args[0], args=flags_args[1])

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute puppet
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=str(Path.cwd()))

    # check idempotence
    if module.params.get('test') and return_code in {2, 4, 6}:
        changed = True
    # enable/disable always cause a change
    elif module.params.get('enable') or module.params.get('disable'):
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
