#!/usr/bin/python
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
    except:
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
        type: dict
    var_file:
        description: HCL2 files containing user variables.
        required: false
        default: {}
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

# validate only the the syntax of the null.this and null.that builds in the packer files
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
      var_name: var_value
      var_name_other: var_value_other
    var_file:
    - one.pkrvars.hcl
    - two.pkrvars.hcl
'''

RETURN = r'''
TODO
'''


def run_module() -> None:



def main() -> None:
    """module entrypoint"""
    run_module()


if __name__ == '__main__':
    main()
