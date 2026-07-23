#!/usr/bin/env bash
# THIS SHOULD ONLY EVER BE EXECUTED FROM WITHIN THIS REPOSITORY'S CI
ansible-galaxy collection build "${REPO_ROOT}"
ansible-galaxy collection install "${TARBALL}"

export ANSIBLE_HOST_KEY_CHECKING=False

for playbook in tests/acceptance/playbooks/*.yml; do
  ansible-playbook -i localhost, $playbook -c local -C
done