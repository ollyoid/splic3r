import pytest
from splic3r import drl

def test_drill():
    drill = drl.DrillFile("")
    assert drill != None

def test_file():
    drill = drl.DrillFile.from_file("tests/drl/PTH.drl")

def test_tools():
    drill = drl.DrillFile.from_file("tests/drl/PTH.drl")
    assert drill.tools == [('T1', 0.3), ('T2', 0.4), ('T3', 0.6), ('T4', 1.0), ('T5', 2.2)]

def test_drills():
    drill = drl.DrillFile.from_file("tests/drl/PTH.drl")
    assert len(drill.drills['T1']) == 68