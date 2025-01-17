#!/usr/bin/env python
from __future__ import division, print_function, unicode_literals, absolute_import

import collections
import os

from pseudo_dojo.core import *
from pseudo_dojo.refdata.nist import database as nist_database


class AtomicConfigurationTest(PseudoDojoTest):

    def test_neutrals(self):
        """Testing neutral configurations."""
        for symbol in nist_database.allsymbols:
            aconf = AtomicConfiguration.neutral_from_symbol(symbol)

            repr(aconf); str(aconf)
            for state in aconf:
                repr(state)
                str(state)

            # Test the shallow copy of states.
            newc = aconf.copy()
            assert newc.states is not aconf.states
            assert newc.states == aconf.states
            assert aconf == newc

            newc.add_state(n=15, l=0, occ=1.0)
            assert aconf != newc

            # Cannot add the same state twice.
            with self.assertRaises(ValueError):
                newc.add_state(n=15, l="s", occ=1.0)

            # aconf is neutral, newc is not.
            assert symbol == aconf.symbol
            assert aconf.isneutral
            assert not newc.isneutral

            assert aconf.spin_mode == "unpolarized"

            # Remove the new state.
            newc.remove_state(n=15, l="s", occ=1.0)
            assert newc.isneutral
            assert aconf == newc

            # Cannot remove the same state twice
            with self.assertRaises(ValueError):
                newc.remove_state(n=15, l="s", occ=1.0)

    def test_initfromstring(self):
        """Initialization of atomic configurations from string"""
        for symbol, confstr in nist_database._neutral.items():
            print("symbol",symbol, confstr)
            Z = nist_database.Z_from_symbol(symbol)
            aconf = AtomicConfiguration.from_string(Z, confstr)

            assert aconf == AtomicConfiguration.neutral_from_symbol(symbol)


class RadialFunctionTest(PseudoDojoTest):

    def test_base(self):
        """Basic tests for RadialFunction."""
        filename = os.path.join(os.path.dirname(__file__), "wf-3s.ape")

        rf = RadialFunction.from_filename(filename)
        rf_der = RadialFunction.from_filename(filename, cols=(0,2))

        repr(rf); str(rf)
        assert isinstance(rf, collections.abc.Iterable)

        # Integral in 3D
        self.assert_almost_equal(rf.integral3d(), 1.0)

        for r, v in rf:
            rf.derivatives(r)

        rslice, vslice = rf[1:4]
        self.assert_equal(rslice, rf.rmesh[1:4])
        self.assert_equal(vslice, rf.values[1:4])
