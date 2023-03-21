#!/usr/bin/python
__metaclass__ = type


from pathlib import Path
from ansible.module_utils.basic import AnsibleModule
from mschuchard.general.plugins.module_utils import goss


DOCUMENTATION = r'''
---
module: goss_render

short_description: Module to render a single valid gossfile.

version_added: "1.0.0"

description: Render a single valid parsed JSON/YAML gossfile.

options:
    debug:
        description: Additionally render the golang template prior to rendering the gossfile.
        required: false
        default: false
        type: bool
    gossfile:
        description: The specific gossfile used for rendering the output.
        required: false
        default: `cwd`/goss.yaml
        type: str

requirements:
    - goss >= 0.3.0

author: Matthew Schuchard (@mschuchard)
'''

EXAMPLES = r'''
# render a gossfile at /path/to/my_gossfile.yaml
- name: Render a gossfile at /path/to/my_gossfile.yaml
  mschuchard.general.goss_render:
    gossfile: /path/to/my_gossfile.yaml

# render a default location gossfile and its corresponding golang template
- name: Render a default location gossfile and its corresponding golang template
  mschuchard.general.goss_render:
    debug: true
'''

RETURN = r'''
TODO
'''


def run_module() -> None:
    """primary function for goss render module"""
    # instanstiate ansible module
    module = AnsibleModule(
        argument_spec=dict(
            debug=dict(type='bool', required=False, default=False),
            gossfile=dict(type='str', required=False, default=Path.cwd())
        ),
        supports_check_mode=True
    )

    # initialize
    changed: bool = False
    gossfile: Path = Path(module.params.get('gossfile'))
    cwd: str = str(Path.cwd())
    if gossfile != Path.cwd():
        cwd = str(Path.parent(gossfile))

    # check on optionl upgrade param
    flags: list[str] = []
    if module.params.get('debug'):
        flags.append('debug')

    # determine goss command
    command: str = goss.cmd(action='render', flags=flags, gossfile=gossfile)

    # exit early for check mode
    if module.check_mode:
        module.exit_json(changed=False, command=command)

    # execute goss
    return_code: int
    stdout: str
    stderr: str
    return_code, stdout, stderr = module.run_command(command, cwd=cwd)

    # check idempotence
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
