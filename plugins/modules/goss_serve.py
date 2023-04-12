#!/usr/bin/python
"""ansible module for goss serve"""
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import goss


DOCUMENTATION = r'''
---
module: goss_serve

short_description: Module to serve a GoSS health endpoint.

version_added: "1.0.0"

description: Serve a GoSS health endpoint for validating systems.

options:
    endpoint:
        description: Endpoint to expose.
        required: false
        default: /healthz
        type: str
    format:
        description: Output format for validation report.
        required: false
        default: rspecish
        type: str
    gossfile:
        description: The specific gossfile used for serveing the output.
        required: false
        default: `cwd`/goss.yaml
        type: str
    port:
        description: Address to listen on.
        required: false
        default: 8080
        type: str
    vars:
        description: Path to YAMl or JSON format file containing variables for template.
        required: false
        type: bool

requirements:
    - goss >= 0.3.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# serve a health endpoint with a gossfile at /path/to/my_gossfile.yaml
- name: Serve a health endpoint with a gossfile at /path/to/my_gossfile.yaml
  mschuchard.general.goss_serve:
    gossfile: /path/to/my_gossfile.yaml

# serve a health endpoint with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
- name: Serve a health endpoint with a default location gossfile, a var file at /path/to/vars.yaml, and a json format output
  mschuchard.general.goss_serve:
    format: json
    vars: /path/to/vars.yaml

# serve a health endpoint with a default location gossfile at localhost:8765/check
- name: Serve a health endpoint with a default location gossfile at localhost:8765/check
  mschuchard.general.goss_serve:
    endpoint: /check
    port: 8765
'''

RETURN = r'''
TODO
'''


def run_module() -> None:
    """primary function for goss serve module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec=dict(
            endpoint={'type': 'str', 'required': False, 'default': ''},
            format={'type': 'str', 'required': False, 'default': ''},
            gossfile={'type': 'path', 'required': False, 'default': Path.cwd()},
            port={'type': 'int', 'required': False, 'default': 0},
            vars={'type': 'str', 'required': False, 'default': Path.cwd()}
        ),
        supports_check_mode=True
    )

    # initialize
    changed: bool = False
    endpoint: str = module.params.get('endpoint')
    the_format: str = module.params.get('format')
    the_vars: Path = Path(module.params.get('vars'))
    port: int = module.params.get('port')
    gossfile: Path = Path(module.params.get('gossfile'))
    cwd: str = str(Path.cwd())
    if gossfile != Path.cwd():
        cwd = str(gossfile.parent)

    # check args
    args: dict = {}
    if len(endpoint) > 0:
        args.update({'endpoint': endpoint})
    if len(the_format) > 0:
        args.update({'format': the_format})
    if port > 0:
        args.update({'port': port})
    if the_vars != Path.cwd():
        args.update({'vars': str(the_vars)})

    # determine goss command
    command: str = goss.cmd(action='serve', args=args, gossfile=gossfile)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute goss
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=cwd)

    # check symbolic idempotence
    if len(stdout) > 0:
        changed = True

    # post-process
    if return_code == 0:
        module.exit_json(changed=changed, stdout=stdout, stderr=stderr, command=command)
    else:
        module.fail_json(
            msg=stderr.rstrip(), return_code=return_code, cmd=command,
            stdout=stdout, stdout_lines=stdout.splitlines(),
            stderr=stderr, stderr_lines=stderr.splitlines())


def main() -> None:
    """module entrypoint"""
    run_module()


if __name__ == '__main__':
    main()
