#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for faas build"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: faas_build

short_description: Module to build a FaaS function container.

version_added: "1.0.0"

description: Builds OpenFaaS function containers either via the supplied YAML config, or via parameters.

options:
    config_file:
        description: Path to YAML file describing function(s)
        required: false
        type: path
    disable_stack_pull:
        description: Disables the template configuration in the stack.yaml
        required: false
        default: false
        type: bool
    env_subst:
        description: Substitute environment variables in stack.yaml file
        required: false
        default: true
        type: bool
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    name:
        description: Name of the deployed function
        required: false
        type: str
    no_cache:
        description: Do not use Docker's build cache
        required: false
        default: false
        type: bool
    pull:
        description: Force a re-pull of base images in template during build, useful for publishing images
        required: false
        default: false
        type: bool
    quiet:
        description: Perform a quiet build, without showing output from Docker
        required: false
        default: false
        type: bool
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    shrinkwrap:
        description: Just write files to ./build/ folder for shrink-wrapping
        required: false
        default: false
        type: bool

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# build a function from a stack.yaml file with no cache, filter, and regex
- name: Build a function from a stack.yaml file with no cache, filter, and regex
  mschuchard.general.faas_build:
    config_file: stack.yaml
    no_cache: True
    filter: '*gif*'
    regex: 'fn[0-9]_.*'

# build a function from a stack.yaml file with pull, shrinkwrap, and disabled stack pull
- name: Build a function from a stack.yaml file with pull, shrinkwrap, and disabled stack pull
  mschuchard.general.faas_build:
    config_file: stack.yaml
    disable_stack_pull: True
    pull: True
    shrinkwrap: True
"""

RETURN = r"""
command:
    description: The raw FaaS CLI command executed by Ansible.
    type: str
    returned: always
"""
