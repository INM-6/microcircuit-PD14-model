# -*- coding: utf-8 -*-
#
# run_microcircuit.py
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
Microcircuit example (Potjans & Diesmann 2014)
----------------------------------------------

Example illustrating usage of the `microcircuit` python package.
"""

import sys
from pathlib import Path

import microcircuit

#####################

## Parameters are read from a YAML override file: everything not listed there
## takes its default from the Parameters class. By default the `params.yaml`
## next to this script is used (it scales the network down to 20 %); an
## alternative file can be passed as the first command line argument:
##
##     python run_microcircuit.py my_params.yaml
##
## `microcircuit.run()` creates and connects the network, simulates it, plots
## the spikes and firing rates, stores the metadata, and prints the timers.
## The command line interface does the same: `microcircuit run --params FILE`.

params_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "params.yaml"

if __name__ == "__main__":
    microcircuit.run(params_file)
