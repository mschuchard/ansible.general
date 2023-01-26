#!/usr/bin/python
__metaclass__ = type


from pathlib import Path


DOCUMENTATION = r'''
---
module: packer_init

short_description: Module to manage Packer template and config directory initialization.

version_added: "1.0.0"

description: Install all the missing plugins required in a Packer config. Note that Packer does not have a state. This is the first command that should be executed when working with a new or existing template. This command is always safe to run multiple times. Though subsequent runs may give errors, this command will never delete anything.

options:
    config_dir:
        description: Location of the directory containing the Packer config file.
        required: false
        default: cwd
        type: str
    upgrade:
        description: Update installed plugins to the latest available version if there is a new higher one. Note that this still considers the version constraint of the config.
        required: false
        default: false
        type: bool

requirements:
    - packer >= 1.7.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# initialize directory in /path/to/packer_config_dir
- name: initialize packer directory in /path/to/packer_config_dir
  mschuchard.general.packer_init:
    config_dir: /path/to/packer_config_dir

# initialize current directory and upgrade plugins
- name: initialize current packer directory and upgrade plugins
  mschuchard.general.packer_init:
    upgrade: true

# initialize directory in /path/to/packer_config_dir and upgrade plugins
- name: initialize packer directory in /path/to/packer_config_dir and upgrade plugins
  mschuchard.general.packer_init:
    config_dir: /path/to/packer_config_dir
    upgrade: true
'''

RETURN = r'''
TODO
'''


from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import packer


def run_module():
    """primary function for packer init module"""
    # define packer_init params
    module_args: dict[str, dict] = dict(
        name=dict(type='str', required=False, default=Path.cwd()),
        new=dict(type='bool', required=False, default=False)
    )

    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check on optionl upgrade param
    flags: list[str] = []
    if module.params['upgrade']:
        flags = ['upgrade']

    # determine packer command
    command: str = packer.cmd(action='init', flags=flags, target_dir=module.params['config_dir'])


def main():
    """module entrypoint"""
    run_module()


if __name__ == '__main__':
    main()
