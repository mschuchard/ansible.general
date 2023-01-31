__metaclass__ = type


import json
import pytest
from mschuchard.general.plugins.modules import packer_init
from mschuchard.general.tests.unit.plugins.modules.utils import set_module_args


def test_packer_init_defaults(capfd):
    set_module_args({})
    packer_init.main()

    stdout, stderr = capfd.readouterr()
    print(stdout)
    print(stderr)
