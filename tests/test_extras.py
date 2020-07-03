# -*- coding: utf-8 -*-
# =============================================================================
#     filter_functions
#     Copyright (C) 2019 Quantum Technology Group, RWTH Aachen University
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#     Contact email: tobias.hangleiter@rwth-aachen.de
# =============================================================================
"""
This module tests if optional extras are handled correctly.
"""
import os

import pytest
from numpy import ndarray

from tests import testutil

all_extras = ['fancy_progressbar', 'plotting', 'bloch_sphere_visualization']


class MissingExtrasTest(testutil.TestCase):

    @pytest.mark.skipif(
        'fancy_progressbar' in os.environ.get('INSTALL_EXTRAS', all_extras),
        reason='Skipping tests for missing fancy progressbar extra in build with requests')  # noqa
    def test_fancy_progressbar_not_available(self):
        from filter_functions import util
        from tqdm import tqdm
        self.assertEqual(util._NOTEBOOK_NAME, '')
        self.assertIs(tqdm, util._tqdm)

    @pytest.mark.skipif(
        'plotting' in os.environ.get('INSTALL_EXTRAS', all_extras),
        reason='Skipping tests for missing plotting extra in build with matplotlib')  # noqa
    def test_plotting_not_available(self):
        with self.assertRaises(ModuleNotFoundError):
            from filter_functions import plotting

    @pytest.mark.skipif(
        'bloch_sphere_visualization' in os.environ.get('INSTALL_EXTRAS', all_extras),  # noqa
        reason='Skipping tests for missing bloch sphere visualization tests in build with qutip')  # noqa
    def test_bloch_sphere_visualization_not_available(self):

        with self.assertWarns(UserWarning):
            from filter_functions import plotting

        with self.assertRaises(RuntimeError):
            plotting.get_bloch_vector(testutil.rng.randn(10, 2))

        with self.assertRaises(RuntimeError):
            plotting.init_bloch_sphere()

        with self.assertRaises(RuntimeError):
            plotting.plot_bloch_vector_evolution(
                testutil.rand_pulse_sequence(2))

        from filter_functions import types
        self.assertIs(types.State, ndarray)
        self.assertIs(types.Operator, ndarray)
