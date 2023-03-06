#!/usr/bin/python
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


def run_module() -> None:
    


def main() -> None:
    """module entrypoint"""
    run_module()


if __name__ == '__main__':
    main()
