#!/usr/bin/env python
# encoding: utf8
# -*- coding: utf-8 -*-
#
# __main__.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
PyNEST implementation of the cortical microcircuit model of Potjans & Diesmann (2014).

Usage: microcircuit [options] run
       microcircuit [options] show_config

Options:
    -p FILE, --params FILE  YAML file with parameter overrides. Parameters not
                            listed in the file take their defaults from the
                            Parameters class. Without this option the small
                            override file shipped with the package is used,
                            which scales the network down to 20 %.
    -v, --verbose           increase output
    -h, --help              print this text
"""

import logging

import pprint
from pprint import pformat
from docopt import docopt  # type: ignore

from microcircuit.parameter_definitions import Parameters, example_params_file
from microcircuit.simulation import run

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def main():
    "Start main CLI entry point."

    args = docopt(__doc__)
    if args["--verbose"]:
        log.setLevel(logging.DEBUG)
    log.debug(pformat(args))

    params_file = args["--params"] or example_params_file()
    log.info("Reading parameter overrides from %s", params_file)
    params = Parameters.from_yaml(params_file)

    if args["run"]:
        run(params)

    if args["show_config"]:
        print()
        print("Model parameters:")
        print("-----------------")
        pprint.pprint(params.model_dump())
        print()


if __name__ == "__main__":
    main()
