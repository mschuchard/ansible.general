#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for faas deploy"""

__metaclass__ = type

DOCUMENTATION = r"""
---
module: faas_deploy

short_description: Module to deploy OpenFaaS function containers.

version_added: "1.3.0"

description: Deploys OpenFaaS function containers either via the supplied YAML config, or via parameters.

options:
    annotation:
        description: Set one or more annotations
        required: false
        type: dict
    config_file:
        description: Path to YAML file describing one or more functions
        required: false
        type: path
    filter:
        description: Wildcard to match with function names in YAML file
        required: false
        type: str
    label:
        description: Set one or more labels
        required: false
        type: dict
    name:
        description: Name of the deployed function
        required: false
        type: str
    regex:
        description: Regex to match with function names in YAML file
        required: false
        type: str
    replace:
        description: Remove and re-create one or more existing functions
        required: false
        type: bool
    update:
        description: Perform rolling update on one or more existing functions
        required: false
        type: bool

requirements:
    - faas-cli >= 0.17.0

author: Matthew Schuchard (@mschuchard)
"""

EXAMPLES = r"""
# deploy a function from a stack.yaml file with function re-creation, filter, and regex
- name: Deploy a function from a stack.yaml file with function re-creation, filter, and regex
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    replace: true
    filter: '*gif*'
    regex: 'fn[0-9]_.*'

# deploy a function from a stack.yaml file with annotations, labels, and no rolling updates
- name: Deploy a function from a stack.yaml file with annotations, labels, and no rolling updates
  mschuchard.general.faas_deploy:
    config_file: stack.yaml
    annotation:
      imageregistry: docker.io
      loadbalancer: mycloud
    label:
      app: myapp
      tier: backend
    update: false
"""

RETURN = r"""
command:
    description: The raw FaaS CLI command executed by Ansible.
    type: str
    returned: always
"""
