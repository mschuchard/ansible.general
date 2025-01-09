#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform apply"""
__metaclass__ = type

DOCUMENTATION = r'''
---
module: terraform_apply

short_description: Module to manage Terraform configuration applications, and update infrastructure accordingly.

version_added: "1.2.0"

description: Creates or updates infrastructure according to Terraform configuration files in the root module directory.

options:
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    destroy:
        description: Destroy Terraform-managed infrastructure.
        required: false
        type: bool
    plan_file:
        description: Location of the output file generated during a plan. Mutually exclusive with all other parameters since the parameters are all defined instead during the plan execution.
        required: false
        type: path
    target:
        description: Limit the applying operation to only the given module, resource, or resource instance, and all of its dependencies.
        required: false
        type: list
    var:
        description: Set values for one or more of the input variables in the root module of the configuration.
        required: false
        type: list
    var_file:
        description: Load variable values from the given HCL2 files in addition to the default files terraform.tfvars and *.auto.tfvars.
        required: false
        type: list


requirements:
    - terraform >= 1.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# destroy infrastructure defined within /path/to/terraform_config_dir
- name: Destroy infrastructure defined within /path/to/terraform_config_dir
  mschuchard.general.terraform_apply:
    config_dir: /path/to/terraform_config_dir
    destroy: true

# apply planned infrastructure changes defined within the plan.tfplan file
- name: Apply planned infrastructure changes defined within the plan.tfplan file
  mschuchard.general.terraform_apply:
      plan_file: plan.tfplan

# apply infrastructures changes to two specific resources with variable inputs
- name: Apply infrastructures changes to two specific resources with variable inputs
  mschuchard.general.terraform_apply:
    target:
    - aws_instance.this
    - local_file.that
    var:
    - var_name: var_value
    - var_name_other: var_value_other
    var_file:
    - one.tfvars
    - two.tfvars
'''

RETURN = r'''
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform apply plan.tfplan'
'''
