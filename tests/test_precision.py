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
This module tests if the package produces the correct results numerically.
"""

import numpy as np
from scipy import linalg as sla

import filter_functions as ff
from filter_functions import analytic, numeric, util
from tests import testutil
from tests.testutil import rng


class PrecisionTest(testutil.TestCase):

    def test_FID(self):
        """FID"""
        tau = abs(rng.standard_normal())
        FID_pulse = ff.PulseSequence([[util.paulis[1]/2, [0]]],
                                     [[util.paulis[3]/2, [1]]],
                                     [tau])

        omega = util.get_sample_frequencies(FID_pulse, 50, spacing='linear')
        # Comparison to filter function defined with omega**2
        F = FID_pulse.get_filter_function(omega).squeeze()*omega**2

        self.assertArrayAlmostEqual(F, analytic.FID(omega*tau), atol=1e-10)

    def test_SE(self):
        """Spin echo"""
        tau = np.pi
        tau_pi = 1e-8
        n = 1

        H_c, dt = testutil.generate_dd_hamiltonian(n, tau=tau, tau_pi=tau_pi,
                                                   dd_type='cpmg')

        H_n = [[util.paulis[3]/2, np.ones_like(dt)]]

        SE_pulse = ff.PulseSequence(H_c, H_n, dt)
        omega = util.get_sample_frequencies(SE_pulse, 100, spacing='linear')
        # Comparison to filter function defined with omega**2
        F = SE_pulse.get_filter_function(omega)[0, 0]*omega**2

        self.assertArrayAlmostEqual(F, analytic.SE(omega*tau), atol=1e-10)

        # Test again with a factor of one between the noise operators and
        # coefficients
        r = rng.standard_normal()
        H_n = [[util.paulis[3]/2*r, np.ones_like(dt)/r]]

        SE_pulse = ff.PulseSequence(H_c, H_n, dt)
        # Comparison to filter function defined with omega**2
        F = SE_pulse.get_filter_function(omega)[0, 0]*omega**2

        self.assertArrayAlmostEqual(F, analytic.SE(omega*tau), atol=1e-10)

    def test_6_pulse_CPMG(self):
        """6-pulse CPMG"""
        tau = np.pi
        tau_pi = 1e-9
        n = 6

        H_c, dt = testutil.generate_dd_hamiltonian(n, tau=tau, tau_pi=tau_pi,
                                                   dd_type='cpmg')

        H_n = [[util.paulis[3]/2, np.ones_like(dt)]]

        CPMG_pulse = ff.PulseSequence(H_c, H_n, dt)
        omega = util.get_sample_frequencies(CPMG_pulse, 100, spacing='log')
        # Comparison to filter function defined with omega**2
        F = CPMG_pulse.get_filter_function(omega)[0, 0]*omega**2

        self.assertArrayAlmostEqual(F, analytic.CPMG(omega*tau, n), atol=1e-10)

    def test_6_pulse_UDD(self):
        """6-pulse UDD"""
        tau = np.pi
        tau_pi = 1e-9
        omega = np.logspace(0, 3, 100)
        omega = np.concatenate([-omega[::-1], omega])
        n = 6

        H_c, dt = testutil.generate_dd_hamiltonian(n, tau=tau, tau_pi=tau_pi,
                                                   dd_type='udd')

        H_n = [[util.paulis[3]/2, np.ones_like(dt)]]

        UDD_pulse = ff.PulseSequence(H_c, H_n, dt)
        # Comparison to filter function defined with omega**2
        F = UDD_pulse.get_filter_function(omega)[0, 0]*omega**2

        self.assertArrayAlmostEqual(F, analytic.UDD(omega*tau, n), atol=1e-10)

    def test_6_pulse_PDD(self):
        """6-pulse PDD"""
        tau = np.pi
        tau_pi = 1e-9
        omega = np.logspace(0, 3, 100)
        omega = np.concatenate([-omega[::-1], omega])
        n = 6

        H_c, dt = testutil.generate_dd_hamiltonian(n, tau=tau, tau_pi=tau_pi,
                                                   dd_type='pdd')

        H_n = [[util.paulis[3]/2, np.ones_like(dt)]]

        PDD_pulse = ff.PulseSequence(H_c, H_n, dt)
        # Comparison to filter function defined with omega**2
        F = PDD_pulse.get_filter_function(omega)[0, 0]*omega**2

        self.assertArrayAlmostEqual(F, analytic.PDD(omega*tau, n), atol=1e-10)

    def test_5_pulse_CDD(self):
        """5-pulse CDD"""
        tau = np.pi
        tau_pi = 1e-9
        omega = np.logspace(0, 3, 100)
        omega = np.concatenate([-omega[::-1], omega])
        n = 3

        H_c, dt = testutil.generate_dd_hamiltonian(n, tau=tau, tau_pi=tau_pi,
                                                   dd_type='cdd')

        H_n = [[util.paulis[3]/2, np.ones_like(dt)]]

        CDD_pulse = ff.PulseSequence(H_c, H_n, dt)
        # Comparison to filter function defined with omega**2
        F = CDD_pulse.get_filter_function(omega)[0, 0]*omega**2

        self.assertArrayAlmostEqual(F, analytic.CDD(omega*tau, n), atol=1e-10)

    def test_diagonalization_cnot(self):
        """CNOT"""
        cnot_mat = np.block([[util.paulis[0], np.zeros((2, 2))],
                             [np.zeros((2, 2)), util.paulis[1]]])

        subspace_c_opers = testutil.subspace_opers
        subspace_n_opers = subspace_c_opers
        c_opers = testutil.opers
        n_opers = c_opers
        c_coeffs, n_coeffs = testutil.c_coeffs, testutil.n_coeffs
        dt = testutil.dt
        subspace = testutil.subspace

        cnot_subspace = ff.PulseSequence(list(zip(subspace_c_opers, c_coeffs)),
                                         list(zip(subspace_n_opers, n_coeffs)),
                                         dt)

        cnot = ff.PulseSequence(list(zip(c_opers, c_coeffs)),
                                list(zip(n_opers, n_coeffs)),
                                dt)

        cnot.diagonalize()
        cnot_subspace.diagonalize()

        phase_eq = ff.util.oper_equiv(cnot_subspace.total_propagator[1:5, 1:5],
                                      cnot_mat, eps=1e-9)

        self.assertTrue(phase_eq[0])

        phase_eq = ff.util.oper_equiv(cnot.total_propagator[np.ix_(*subspace)][1:5, 1:5],
                                      cnot_mat, eps=1e-9)

        self.assertTrue(phase_eq[0])

    def test_infidelity_cnot(self):
        """Compare infidelity to monte carlo results"""
        c_opers = testutil.subspace_opers
        n_opers = c_opers
        c_coeffs, n_coeffs = testutil.c_coeffs, testutil.n_coeffs
        dt = testutil.dt
        infid_MC = testutil.cnot_infid_fast
        A = testutil.A

        # Basis for qubit subspace
        qubit_subspace_basis = ff.Basis(
            [np.pad(b, 1, 'constant') for b in ff.Basis.pauli(2)[1:]],
            skip_check=True,
            btype='Pauli'
        )
        complete_basis = ff.Basis(qubit_subspace_basis, traceless=False,
                                  btype='Pauli')

        identifiers = ['eps_12', 'eps_23', 'eps_34', 'b_12', 'b_23', 'b_34']
        H_c = list(zip(c_opers, c_coeffs, identifiers))
        H_n = list(zip(n_opers, n_coeffs, identifiers))
        cnot = ff.PulseSequence(H_c, H_n, dt, basis=qubit_subspace_basis)
        cnot_full = ff.PulseSequence(H_c, H_n, dt, basis=complete_basis)

        # Manually set dimension of pulse as the dimension of the computational
        # subspace
        cnot.d = 4
        f_min = 1/cnot.tau
        omega = np.geomspace(f_min, 1e2, 250)

        for A, alpha, MC in zip(A, (0.0, 0.7), infid_MC):
            S = A/omega**alpha

            infid, xi = ff.infidelity(cnot, S, omega, identifiers[:3],
                                      return_smallness=True)

            K = numeric.calculate_cumulant_function(cnot_full, S, omega,
                                                    identifiers[:3])
            infid_P = - np.trace(K[:, :16, :16], axis1=1, axis2=2).real/4**2

            self.assertLessEqual(np.abs(1 - (infid.sum()/MC)), 0.10)
            self.assertLessEqual(np.abs(1 - (infid_P.sum()/MC)), 0.10)
            self.assertLessEqual(infid.sum(), xi**2/4)

    def test_calculation_with_unitaries(self):
        for d, G in zip(rng.randint(2, 9, (11,)), rng.randint(2, 11, (11,))):
            pulses = [testutil.rand_pulse_sequence(d, rng.randint(1, 11), 2, 4)
                      for g in range(G)]

            for pulse in pulses:
                # All pulses should have same n_opers for xxx_from_atomic
                pulse.n_opers = pulses[0].n_opers
                pulse.n_oper_identifiers = pulses[0].n_oper_identifiers
                if rng.randint(0, 2):
                    pulse.t = None

            omega = rng.rand(17)
            B_atomic = np.array([numeric.calculate_noise_operators_from_scratch(
                pulse.eigvals, pulse.eigvecs, pulse.propagators, omega, pulse.n_opers,
                pulse.n_coeffs, pulse.dt, pulse.t
            ) for pulse in pulses])

            R_atomic = np.array([numeric.calculate_control_matrix_from_scratch(
                pulse.eigvals, pulse.eigvecs, pulse.propagators, omega, pulse.basis,
                pulse.n_opers, pulse.n_coeffs, pulse.dt, pulse.t
            ) for pulse in pulses])

            self.assertArrayAlmostEqual(ff.basis.expand(B_atomic, pulse.basis),
                                        R_atomic.transpose(0, 3, 1, 2),
                                        atol=1e-14)

            B = numeric.calculate_noise_operators_from_atomic(
                np.array([pulse.get_total_phases(omega) for pulse in pulses]),
                B_atomic,
                np.array([pulse.total_propagator for pulse in pulses])
            )

            R = numeric.calculate_control_matrix_from_atomic(
                np.array([pulse.get_total_phases(omega) for pulse in pulses]),
                R_atomic,
                np.array([pulse.total_propagator_liouville for pulse in pulses])
            )

            self.assertArrayAlmostEqual(ff.basis.expand(B, pulse.basis),
                                        R.transpose(2, 0, 1),
                                        atol=1e-14)

    def test_integration(self):
        """Test the private function used to set up the integrand."""
        pulses = [testutil.rand_pulse_sequence(3, 1, 2, 3),
                  testutil.rand_pulse_sequence(3, 1, 2, 3)]
        pulses[1].n_opers = pulses[0].n_opers
        pulses[1].n_oper_identifiers = pulses[0].n_oper_identifiers

        omega = np.linspace(-1, 1, 50)
        spectra = [
            1e-6/abs(omega),
            1e-6/np.power.outer(abs(omega), np.arange(2)).T,
            np.array([[1e-6/abs(omega)**0.7,
                       1e-6/(1 + omega**2) + 1j*1e-6*omega],
                      [1e-6/(1 + omega**2) - 1j*1e-6*omega,
                       1e-6/abs(omega)**0.7]])
        ]

        pulse = ff.concatenate(pulses, omega=omega,
                               calc_pulse_correlation_FF=True)

        idx = testutil.rng.choice(np.arange(2), testutil.rng.randint(1, 3),
                                  replace=False)

        R = pulse.get_control_matrix(omega)
        R_pc = pulse.get_pulse_correlation_control_matrix()
        F = pulse.get_filter_function(omega)
        F_kl = pulse.get_filter_function(omega, 'generalized')
        F_pc = pulse.get_pulse_correlation_filter_function()
        F_pc_kl = pulse.get_pulse_correlation_filter_function('generalized')

        for i, spectrum in enumerate(spectra):
            if i == 0:
                S = spectrum
            elif i == 1:
                S = spectrum[idx]
            elif i == 2:
                S = spectrum[idx[None, :], idx[:, None]]

            R_1 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='total',
                                         which_FF='fidelity',
                                         control_matrix=R,
                                         filter_function=None)
            R_2 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='total',
                                         which_FF='fidelity',
                                         control_matrix=[R, R],
                                         filter_function=None)
            F_1 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='total',
                                         which_FF='fidelity',
                                         control_matrix=None,
                                         filter_function=F)

            self.assertArrayAlmostEqual(R_1, R_2)
            self.assertArrayAlmostEqual(R_1, F_1)

            R_1 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='correlations',
                                         which_FF='fidelity',
                                         control_matrix=R_pc,
                                         filter_function=None)
            R_2 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='correlations',
                                         which_FF='fidelity',
                                         control_matrix=[R_pc, R_pc],
                                         filter_function=None)
            F_1 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='correlations',
                                         which_FF='fidelity',
                                         control_matrix=None,
                                         filter_function=F_pc)

            self.assertArrayAlmostEqual(R_1, R_2)
            self.assertArrayAlmostEqual(R_1, F_1)

            R_1 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='total',
                                         which_FF='generalized',
                                         control_matrix=R,
                                         filter_function=None)
            R_2 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='total',
                                         which_FF='generalized',
                                         control_matrix=[R, R],
                                         filter_function=None)
            F_1 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='total',
                                         which_FF='generalized',
                                         control_matrix=None,
                                         filter_function=F_kl)

            self.assertArrayAlmostEqual(R_1, R_2)
            self.assertArrayAlmostEqual(R_1, F_1)

            R_1 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='correlations',
                                         which_FF='generalized',
                                         control_matrix=R_pc,
                                         filter_function=None)
            R_2 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='correlations',
                                         which_FF='generalized',
                                         control_matrix=[R_pc, R_pc],
                                         filter_function=None)
            F_1 = numeric._get_integrand(S, omega, idx,
                                         which_pulse='correlations',
                                         which_FF='generalized',
                                         control_matrix=None,
                                         filter_function=F_pc_kl)

            self.assertArrayAlmostEqual(R_1, R_2)
            self.assertArrayAlmostEqual(R_1, F_1)

    def test_infidelity(self):
        """Benchmark infidelity results against previous version's results"""
        rng.seed(123456789)

        spectra = [
            lambda S0, omega: S0*abs(omega)**0,
            lambda S0, omega: S0/abs(omega)**0.7,
            lambda S0, omega: S0*np.exp(-abs(omega)),
            # different spectra for different n_opers
            lambda S0, omega: np.array([S0*abs(omega)**0, S0/abs(omega)**0.7]),
            # cross-correlated spectra
            lambda S0, omega: np.array(
                [[S0/abs(omega)**0.7, S0/(1 + omega**2) + 1j*S0*omega],
                 [S0/(1 + omega**2) - 1j*S0*omega, S0/abs(omega)**0.7]]
            )
        ]

        ref_infids = (
            [[0.415494970094, 0.89587362496],
             [0.493004378474, 0.812378971328],
             [0.133466914361, 0.197411969384],
             [0.415494970094, 0.812378971328],
             [[0.493004378474, 0.435140425045],
              [0.435140425045, 0.812378971328]],
             [3.62995021962, 2.938710386281],
             [2.302617869945, 2.6187737025],
             [0.506821680978, 0.695495602872],
             [3.62995021962, 2.6187737025],
             [[2.302617869945, 0.58515469294],
              [0.58515469294, 2.6187737025]],
             [2.822636459567, 1.205901937127],
             [1.63758822101, 1.236844976323],
             [0.324175447082, 0.329789052239],
             [2.822636459567, 1.236844976323],
             [[1.63758822101, 0.72007826813],
              [0.72007826813, 1.236844976323]]]
        )

        count = 0
        for d in (2, 3, 4):
            pulse = testutil.rand_pulse_sequence(d, 10, 2, 3)
            pulse.n_oper_identifiers = np.array(['B_0', 'B_2'])

            omega = np.geomspace(0.1, 10, 51)
            S0 = np.abs(rng.standard_normal())
            for spec in spectra:
                S = spec(S0, omega)
                infids = ff.infidelity(pulse, S, omega,
                                       n_oper_identifiers=['B_0', 'B_2'])
                self.assertArrayAlmostEqual(infids, ref_infids[count],
                                            atol=1e-12)
                if S.ndim == 3:
                    # Diagonal of the infidelity matrix should correspond to
                    # uncorrelated terms
                    uncorrelated_infids = ff.infidelity(
                        pulse, S[range(2), range(2)], omega,
                        n_oper_identifiers=['B_0', 'B_2']
                    )
                    self.assertArrayAlmostEqual(np.diag(infids),
                                                uncorrelated_infids)

                    # Infidelity matrix should be hermitian
                    self.assertArrayEqual(infids, infids.conj().T)

                count += 1

        # Check raises
        with self.assertRaises(TypeError):
            # spectrum not callable
            ff.infidelity(pulse, 2, omega, test_convergence=True)

        with self.assertRaises(TypeError):
            # omega not dict
            ff.infidelity(pulse, lambda x: x, 2, test_convergence=True)

        with self.assertRaises(ValueError):
            # omega['spacing'] not in ('linear', 'log')
            ff.infidelity(pulse, lambda x: x, {'spacing': 2},
                          test_convergence=True)

        with self.assertRaises(ValueError):
            # which not total or correlation
            ff.infidelity(pulse, spectra[0](S0, omega), omega, which=2)

        with self.assertRaises(ValueError):
            # S wrong dimensions
            ff.infidelity(pulse, spectra[0](S0, omega)[:10], omega)

        with self.assertRaises(ValueError):
            # S wrong dimensions
            ff.infidelity(pulse, spectra[3](S0, omega), omega,
                          n_oper_identifiers=['B_0', 'B_1', 'B_2'])

        with self.assertRaises(ValueError):
            # S wrong dimensions
            ff.infidelity(pulse, spectra[4](S0, omega)[:, [0]], omega,
                          n_oper_identifiers=['B_0'])

        with self.assertRaises(ValueError):
            # S wrong dimensions
            ff.infidelity(pulse, rng.standard_normal((2, 3, 4, len(omega))),
                          omega)

        with self.assertRaises(NotImplementedError):
            # smallness parameter for correlated noise source
            ff.infidelity(pulse, spectra[4](S0, omega), omega,
                          n_oper_identifiers=['B_0', 'B_2'],
                          return_smallness=True)

    def test_single_qubit_error_transfer_matrix(self):
        """Test the calculation of the single-qubit transfer matrix"""
        d = 2
        for n_dt in rng.randint(1, 11, 10):
            pulse = testutil.rand_pulse_sequence(d, n_dt, 3, 2, btype='Pauli')
            omega = util.get_sample_frequencies(pulse, n_samples=51)
            n_oper_identifiers = pulse.n_oper_identifiers
            traces = pulse.basis.four_element_traces.todense()

            # Single spectrum
            # Assert fidelity is same as computed by infidelity()
            S = 1e-8/omega**2
            U = ff.error_transfer_matrix(pulse, S, omega)
            # Calculate U in loop
            Up = ff.error_transfer_matrix(pulse, S, omega,
                                          memory_parsimonious=True)
            # Calculate on foot (multi-qubit way)
            Gamma = numeric.calculate_decay_amplitudes(pulse, S, omega,
                                                       n_oper_identifiers)
            K = -(np.einsum('...kl,klji->...ij', Gamma, traces) -
                  np.einsum('...kl,kjli->...ij', Gamma, traces) -
                  np.einsum('...kl,kilj->...ij', Gamma, traces) +
                  np.einsum('...kl,kijl->...ij', Gamma, traces))/2
            U_onfoot = sla.expm(K.sum(0))
            U_from_K = ff.error_transfer_matrix(cumulant_function=K)
            I_fidelity = ff.infidelity(pulse, S, omega)
            I_decayamps = -np.einsum('...ii', K)/d**2
            I_transfer = 1 - np.einsum('...ii', U)/d**2
            self.assertArrayAlmostEqual(Up, U)
            self.assertArrayAlmostEqual(I_fidelity, I_decayamps)
            self.assertArrayAlmostEqual(I_transfer, I_fidelity.sum(),
                                        rtol=1e-4)
            self.assertArrayAlmostEqual(U, U_onfoot, atol=1e-14)
            self.assertArrayAlmostEqual(U_from_K, U_onfoot)

            # Different spectra for each noise oper
            S = np.outer(1e-6*np.arange(1, 3), 400/(omega**2 + 400))
            U = ff.error_transfer_matrix(pulse, S, omega)
            Up = ff.error_transfer_matrix(pulse, S, omega,
                                          memory_parsimonious=True)
            Gamma = numeric.calculate_decay_amplitudes(pulse, S, omega,
                                                       n_oper_identifiers)
            K = -(np.einsum('...kl,klji->...ij', Gamma, traces) -
                  np.einsum('...kl,kjli->...ij', Gamma, traces) -
                  np.einsum('...kl,kilj->...ij', Gamma, traces) +
                  np.einsum('...kl,kijl->...ij', Gamma, traces))/2
            U_onfoot = sla.expm(K.sum(0))
            U_from_K = ff.error_transfer_matrix(cumulant_function=K)
            I_fidelity = ff.infidelity(pulse, S, omega)
            I_decayamps = -np.einsum('...ii', K)/d**2
            I_transfer = 1 - np.einsum('...ii', U)/d**2
            self.assertArrayAlmostEqual(Up, U)
            self.assertArrayAlmostEqual(I_fidelity, I_decayamps)
            self.assertArrayAlmostEqual(I_transfer, I_fidelity.sum(),
                                        rtol=1e-4)
            self.assertArrayAlmostEqual(U, U_onfoot, atol=1e-14)
            self.assertArrayAlmostEqual(U_from_K, U_onfoot)

            # Cross-correlated spectra are complex, real part symmetric and
            # imaginary part antisymmetric
            S = np.array([[1e-6/abs(omega), 1e-8/abs(omega) + 1j*1e-8/omega],
                          [1e-8/abs(omega) - 1j*1e-8/omega, 2e-6/abs(omega)]])
            U = ff.error_transfer_matrix(pulse, S, omega)
            Up = ff.error_transfer_matrix(pulse, S, omega,
                                          memory_parsimonious=True)
            Gamma = numeric.calculate_decay_amplitudes(pulse, S, omega,
                                                       n_oper_identifiers)
            K = -(np.einsum('...kl,klji->...ij', Gamma, traces) -
                  np.einsum('...kl,kjli->...ij', Gamma, traces) -
                  np.einsum('...kl,kilj->...ij', Gamma, traces) +
                  np.einsum('...kl,kijl->...ij', Gamma, traces))/2
            U_onfoot = sla.expm(K.sum((0, 1)))
            U_from_K = ff.error_transfer_matrix(cumulant_function=K)
            I_fidelity = ff.infidelity(pulse, S, omega)
            I_decayamps = -np.einsum('...ii', K)/d**2
            I_transfer = 1 - np.einsum('...ii', U)/d**2
            self.assertArrayAlmostEqual(Up, U)
            self.assertArrayAlmostEqual(I_fidelity, I_decayamps)
            self.assertArrayAlmostEqual(I_transfer, I_fidelity.sum(),
                                        rtol=1e-4)
            self.assertArrayAlmostEqual(U, U_onfoot, atol=1e-14)
            self.assertArrayAlmostEqual(U_from_K, U_onfoot)

    def test_multi_qubit_error_transfer_matrix(self):
        """Test the calculation of the multi-qubit transfer matrix"""
        n_cops = 4
        n_nops = 2
        for d, n_dt in zip(rng.randint(3, 9, 10), rng.randint(1, 11, 10)):
            f, n = np.modf(np.log2(d))
            btype = 'Pauli' if f == 0.0 else 'GGM'
            pulse = testutil.rand_pulse_sequence(d, n_dt, n_cops, n_nops,
                                                 btype)
            omega = util.get_sample_frequencies(pulse, n_samples=51)

            # Assert fidelity is same as computed by infidelity()
            S = 1e-8/omega**2
            U = ff.error_transfer_matrix(pulse, S, omega)
            # Calculate U in loop
            Up = ff.error_transfer_matrix(pulse, S, omega,
                                          memory_parsimonious=True)
            I_fidelity = ff.infidelity(pulse, S, omega)
            I_transfer = 1 - np.einsum('...ii', U)/d**2
            self.assertArrayAlmostEqual(Up, U)
            self.assertArrayAlmostEqual(I_transfer, I_fidelity.sum(),
                                        atol=1e-4)

            S = np.outer(1e-7*(np.arange(n_nops) + 1),
                         400/(omega**2 + 400))
            U = ff.error_transfer_matrix(pulse, S, omega)
            # Calculate U in loop
            Up = ff.error_transfer_matrix(pulse, S, omega,
                                          memory_parsimonious=True)
            I_fidelity = ff.infidelity(pulse, S, omega)
            I_transfer = 1 - np.einsum('...ii', U)/d**2
            self.assertArrayAlmostEqual(Up, U)
            self.assertArrayAlmostEqual(I_transfer, I_fidelity.sum(),
                                        atol=1e-4)

            S = np.tile(1e-8/abs(omega)**2, (n_nops, n_nops, 1)).astype(
                complex)
            S[np.triu_indices(n_nops, 1)].imag = 1e-10*omega
            S[np.tril_indices(n_nops, -1)].imag = \
                - S[np.triu_indices(n_nops, 1)].imag
            U = ff.error_transfer_matrix(pulse, S, omega)
            # Calculate U in loop
            Up = ff.error_transfer_matrix(pulse, S, omega,
                                          memory_parsimonious=True)
            I_fidelity = ff.infidelity(pulse, S, omega)
            I_transfer = 1 - np.einsum('...ii', U)/d**2
            self.assertArrayAlmostEqual(Up, U)
            self.assertArrayAlmostEqual(I_transfer, I_fidelity.sum(),
                                        atol=1e-4)
