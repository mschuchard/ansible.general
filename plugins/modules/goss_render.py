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



def main() -> None:
    """module entrypoint"""
    run_module()


if __name__ == '__main__':
    main()
