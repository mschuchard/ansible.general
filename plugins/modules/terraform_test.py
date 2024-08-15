#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Matthew Schuchard
# MIT License (see LICENSE or https://opensource.org/license/mit)
"""ansible module for terraform test"""
__metaclass__ = type

DOCUMENTATION = r'''
---
module: terraform_test

short_description: Module to manage Terraform automated integration tests against current configuration.

version_added: "1.1.0"

description: Executes automated integration tests against the current Terraform configuration. Terraform will search for .tftest.hcl files within the current configuration and testing directories. Terraform will then execute the testing run blocks within any testing files in order, and verify conditional checks and assertions against the created infrastructure. This command creates real infrastructure and will attempt to clean up the testing infrastructure on completion. Monitor the output carefully to ensure this cleanup process is successful.

options:
    cloud_run:
        description: Terraform will execute this test run remotely using HCP Terraform or Terraform Enterpise. You must specify the source of a module registered in a private module registry as the argument to this parameter. This allows Terraform to associate the cloud run with the correct HCP Terraform or Terraform Enterprise module and organization.
        required: false
        type: str
    config_dir:
        description: Location of the directory containing the Terraform root module config files.
        required: false
        default: cwd
        type: path
    filter:
        description: Terraform will only execute the test files specified by this parameter.
        required: false
        default: []
        type: list
    json:
        description: Machine readable output will be output to stdout in JSON format.
        required: false
        default: false
        type: bool
    test_dir:
        description: Set the Terraform test directory.
        required: false
        default: tests
        type: path
    var:
        description: Set values for one or more of the input variables in the root module of the configuration.
        required: false
        default: []
        type: list
    var_file:
        description: Load variable values from the given HCL2 files in addition to the default files terraform.tfvars and *.auto.tfvars.
        required: false
        default: []
        type: list


requirements:
    - terraform >= 1.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# execute tests in /path/to/terraform_config_dir/my_tests
- name: Execute tests in /path/to/terraform_config_dir/my_tests
  mschuchard.general.terraform_test:
    config_dir: /path/to/terraform_config_dir
    test_dir: my_tests

# execute tests for current directory with json output and variable inputs
- name: Execute tests for current directory with json output and variable inputs
  mschuchard.general.terraform_test:
    json: true
    var:
    - var_name: var_value
    - var_name_other: var_value_other
    var_file:
    - one.pkrvars.hcl
    - two.pkrvars.hcl
'''

RETURN = r'''
command:
    description: The raw Terraform command executed by Ansible.
    type: str
    returned: always
    sample: 'terraform test -json'
'''
