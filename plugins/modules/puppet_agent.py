#!/usr/bin/python
"""ansible module for puppet agent"""
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import puppet


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
    no_op:
        description: Use 'noop' mode where Puppet runs in a no-op or dry-run mode. This is useful for seeing what changes Puppet will make without actually executing the changes.
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
'''

RETURN = r'''
command:
    description: The raw Puppet command executed by Ansible.
    type: str
    returned: always
'''
