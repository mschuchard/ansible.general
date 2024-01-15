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
