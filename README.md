# mschuchard.general Ansible Collection

This repository contains the `mschuchard.general` collection. This collection primarily contains module plugins that support tools commonly considered part of the "DevOps" ecosystem. The tools to be supported are chosen either because no current module plugin support exists, or there are feature requests and functionality gaps for any current module plugins supporting those tools.

**Supported Tools**
- [GoSS](https://github.com/goss-org/goss)
- [Packer](https://www.packer.io/)
- [Puppet](https://www.puppet.com/)

## Documentation

Documentation is generated from Python docstrings with expected Ansible plugin formatting. Please consult the generated documentation at [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/mschuchard/general/docs).

## Requirements

This collection requires Ansible `>= 2.12`, and Python `>= 3.10`.

Each module plugin also requires a functioning installation on the target system of the tool with which it is interfacing. This collection functionality does not include the software tool installation.

## Usage

You can install the collection from [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/mschuchard/general) manually with the `ansible-galaxy` command-line tool:

`ansible-galaxy collection install community.general`

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: mschuchard.general
```

The above file would need to be located in `collections/requirements.yml` for automatic parsing by an [Ansible Automation Platform Controller Project](https://docs.ansible.com/automation-controller/latest/html/userguide/projects.html#collections-support).

See [Ansible Using Collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing
Code should pass all unit tests. New features should involve new unit tests.

Please consult the GitHub Project for the current development roadmap.
