#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform plan"""
__metaclass__ = type

DOCUMENTATION = r'''
---
module: terraform_test

short_description: Module to manage Terraform speculative execution plans, and show what actions Terraform would take to apply the current configuration.

version_added: "1.2.0"

description: Generates a speculative execution plan showing what actions Terraform would take to apply the current configuration. This module will not actually perform the planned actions.

options:
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    destroy:
        description: Select the destroy planning mode which creates a plan to destroy all objects currently managed by this Terraform configuration instead of the usual behavior.
        required: false
        type: bool
    generate_config:
        description: If import blocks are present in configuration, then instructs Terraform to generate HCL for any imported resources not already present. The configuration is written to a new file at the parameter value which must not already exist. Terraform may still attempt to write configuration if the plan errors.
        required: false
        type: str
    out:
        description: Write a plan file to the given parameter value. This can be used as input to the apply module.
        required: false
        type: str
    refresh_only:
        description: Select the refresh only planning mode which checks whether remote objects still match the outcome of the most recent Terraform apply, but does not propose any actions to undo any changes made outside of Terraform.
        required: false
        type: bool
    replace:
        description: Force replacement of a particular resource instance using its resource address. If the plan would normally produce an update or no-op action for this instance, then Terraform will plan to replace it instead.
        required: false
        type: list
    target:
        description: Limit the planning operation to only the given module, resource, or resource instance, and all of its dependencies.
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
# produce destroy plan for /path/to/terraform_config_dir
- name: Produce destroy plan for /path/to/terraform_config_dir
  mschuchard.general.terraform_plan:
    config_dir: /path/to/terraform_config_dir
    destroy: true

# produce plan that replaces two resources, and output the result to plan.tfplan
- name: Produce plan that replaces two resources, and output the result to plan.tfplan
  mschuchard.general.terraform_plan:
    replace:
    - aws_instance.this
    - local_file.that
    out: plan.tfplan

# produce plan to check configuration drift with variable inputs
- name: Produce plan to check configuration drift with variable inputs
  mschuchard.general.terraform_plan:
    refresh_only: true
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
    sample: 'terraform plan -out plan.tfplan'
'''
