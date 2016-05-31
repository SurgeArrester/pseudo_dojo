"""Integration tests for EbandsFactory."""
from __future__ import print_function, division, unicode_literals, absolute_import

import pytest
import pseudo_dojo.data as pdj_data
import abipy.abilab as abilab

from pseudo_dojo.dojo.works import EbandsFactory


def itest_ebands_gga_pawxml_flow(fwp, tvars):
    """Testing the ebands flow for PAW-XML"""
    pseudo = pdj_data.pseudo("Si.GGA_PBE-JTH-paw.xml").as_tmpfile()
    assert pseudo is not None
    print(pseudo)
    assert pseudo.has_dojo_report
    assert not pseudo.dojo_report.exceptions
    spin_mode = "unpolarized"

    flow = abilab.Flow(workdir=fwp.workdir, manager=fwp.manager)
    ebands_factory = EbandsFactory(xc=pseudo.xc)

    ecut = 6
    pawecutdg = 2 * ecut if pseudo.ispaw else None
    work = ebands_factory.work_for_pseudo(pseudo, kppa=20, max_ene=5, ecut=ecut, pawecutdg=pawecutdg,
                                          spin_mode=spin_mode)
    flow.register_work(work)
    flow.build_and_pickle_dump()

    # Validate inputs.
    isok, errors = flow.abivalidate_inputs()
    if not isok:
        print("abivalidate returned errors")
        for i, e in enumerate(errors): print("[%d] %s" % (i, e))
        assert 0

    fwp.scheduler.add_flow(flow)
    assert fwp.scheduler.start() == 0
    assert not fwp.scheduler.exceptions

    flow.check_status(show=True)
    assert all(work.finalized for work in flow)
    assert flow.all_ok

    assert not pseudo.dojo_report.exceptions
    assert pseudo.dojo_report.has_trial("ebands", ecut=ecut)
    d = pseudo.dojo_report["ebands"]["%.1f" % ecut]["ebands"]
    ebands = abilab.ElectronBands.from_dict(d)

    #fig = pseudo.dojo_report.plot_ebands(ecut=ecut, show=False)
    #assert fig is not None


def itest_ebands_gga_ncsoc_flow(fwp, tvars):
    """Testing the ebands flow for NC+SOC pseudos."""
    return
    pseudo = pdj_data.pseudo("Pb-d-3_r.psp8").as_tmpfile()
    assert pseudo is not None
    print(pseudo)
    assert pseudo.has_dojo_report
    assert pseudo.supports_soc
    assert not pseudo.dojo_report.exceptions

    spin_mode = "spinor"

    flow = abilab.Flow(workdir=fwp.workdir, manager=fwp.manager)
    ebands_factory = EbandsFactory(xc=pseudo.xc)

    ecut = 4
    pawecutdg = 2 * ecut if pseudo.ispaw else None
    kppa = 20  # this value is for testing purpose
    work = ebands_factory.work_for_pseudo(pseudo, kppa=kppa, max_ene=2, ecut=ecut, pawecutdg=pawecutdg,
                                          spin_mode=spin_mode)
    flow.register_work(work)
    flow.build_and_pickle_dump()

    # Validate inputs.
    isok, errors = flow.abivalidate_inputs()
    if not isok:
        print("abivalidate returned errors")
        for i, e in enumerate(errors): print("[%d] %s" % (i, e))
        assert 0

    fwp.scheduler.add_flow(flow)
    assert fwp.scheduler.start() == 0
    assert not fwp.scheduler.exceptions

    flow.check_status(show=True)
    assert all(work.finalized for work in flow)
    assert flow.all_ok

    # Reconstruct ElectronBands from JSON.
    assert not pseudo.dojo_report.exceptions
    assert pseudo.dojo_report.has_trial("ebands", ecut=ecut)
    d = pseudo.dojo_report["ebands"]["%.1f" % ecut]["ebands"]
    ebands = abilab.ElectronBands.from_dict(d)

    #fig = pseudo.dojo_report.plot_ebands(ecut=ecut, show=False)
    #assert fig is not None
