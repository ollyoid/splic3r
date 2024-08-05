import pytest
from splic3r import GCode, PrinterState
from copy import copy

# def test_read_gcode_file():
#    gcode = GCode.from_file('tests/gcode/box.gcode')

gcode_str = """G1 Z22 F600
G1 E.8 F1500
M204 P2500
;TYPE:Internal infill
;WIDTH:0.45
G1 F7694
G1 X135.599 Y58.092 E.0677
G1 X138.898 Y61.391 E.15792
"""

def test_gcode_from_string():
    gcode = GCode(gcode_str)
    assert gcode.line_count == 8

def test_gcode_linecount():
    gcode = GCode.from_file('tests/gcode/empty.gcode')
    assert gcode.line_count == 4
    gcode = GCode.from_file('tests/gcode/box.gcode')
    assert gcode.line_count == 23375
    # gcode = GCode.from_file('tests/gcode/multi.gcode')
    # assert gcode.line_count == 294548

def test_interpret_comment():
    printer_state = PrinterState()
    expected_state = PrinterState()
    comment = ";TYPE:Internal infill"
    printer_state.interpret_comment(comment)
    pass

def test_variable_comment():
    my_string = """; external perimeters extrusion width = 0.45mm
    ; perimeters extrusion width = 0.45mm
    ; infill extrusion width = 0.45mm
    ; solid infill extrusion width = 0.45mm
    ; top infill extrusion width = 0.40mm
    ; first layer extrusion width = 0.50mm
    """
    printer_state = PrinterState()
    for line in my_string.splitlines():
        printer_state.interpret_comment(line)
    assert printer_state.var_dict["external perimeters extrusion width"] == "0.45mm"
    assert printer_state.var_dict["perimeters extrusion width"] == "0.45mm"
    assert printer_state.var_dict["infill extrusion width"] == "0.45mm"
    assert printer_state.var_dict["solid infill extrusion width"] == "0.45mm"
    assert printer_state.var_dict["top infill extrusion width"] == "0.40mm"
    assert printer_state.var_dict["first layer extrusion width"] == "0.50mm"


def test_layer_change_comment():
    printer_state = PrinterState()
    for i in range(20):
        printer_state.interpret_comment(";LAYER_CHANGE")
    assert printer_state.layer == 20

def test_layer_height_comment():
    printer_state = PrinterState()
    printer_state.interpret_comment(";Z:3.6")
    assert printer_state.layer_height == 3.6


def test_split_command():
    gcode = GCode()
    assert gcode.split_command('G1 X135.599 Y58.092 E.0677') == ['G1', 'X135.599', 'Y58.092', 'E.0677']
    assert gcode.split_command('G1X135.599Y58.092E.0677') == ['G1', 'X135.599', 'Y58.092', 'E.0677']
    assert gcode.split_command('  G1X135.599  Y58.092E.0677') == ['G1', 'X135.599', 'Y58.092', 'E.0677']
    assert gcode.split_command('  G1X135.599  Y58.092E.0677') == ['G1', 'X135.599', 'Y58.092', 'E.0677']
    # Negative numbers
    assert gcode.split_command('  G1X135.599Y-58.092E.0677') == ['G1', 'X135.599', 'Y-58.092', 'E.0677']

def test_execute_command():
    printer_state = PrinterState()
    expected_state = PrinterState()
    expected_state.current_position = [135.599, 58.092,0]
    expected_state.amount_extruded = .0677
    expected_state.extruding =True
    assert printer_state.execute_command(['G1', 'X135.599', 'Y58.092', 'E.0677']) == expected_state
    expected_state.feedrate = 1000
    expected_state.extruding =False
    assert printer_state.execute_command(['G1', 'F1000']) == expected_state
    printer_state = copy(expected_state)
    printer_state.relative = True
    expected_state.relative = True
    expected_state.current_position = [0, 58.092,0]
    assert printer_state.execute_command(['G1', 'X-135.599']) == expected_state


def test_G2_G3():
    printer_state = PrinterState()
    expected_state = PrinterState()
    expected_state.current_position = [10,20.05,0]
    expected_state.amount_extruded = 0.304
    expected_state.extruding =True
    assert printer_state.execute_command(['G2', 'X10', 'Y20.05', 'E.304']) == expected_state
    expected_state.current_position = [4,20.05,0]
    expected_state.amount_extruded = 0.608
    assert printer_state.execute_command(['G3', 'X4', 'Y20.05', 'E.304']) == expected_state	
    

def test_G28():
    printer_state = PrinterState()
    expected_state = PrinterState()
    printer_state.execute_command(['G1', 'X19', 'Y5.2', 'E.7'])
    printer_state.execute_command(['G28'])
    expected_state.amount_extruded = 0.7
    assert printer_state == expected_state
    printer_state.execute_command(['G1', 'X19', 'Y5.2', 'E.7'])
    printer_state.execute_command(['G28', 'X'])
    expected_state.current_position = [0,5.2,0]
    expected_state.amount_extruded = 1.4
    assert printer_state == expected_state

args = None

def test_G92():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement G92 command
    printer_state.execute_command(['G1', 'X30', 'Y5', 'E7'])
    printer_state.execute_command(['G92', 'X30', 'Y', 'E0'])
    expected_state.current_position = [30,0,0]
    expected_state.amount_extruded = 0
    expected_state.origin_offset = [0,5,0]
    expected_state.extrude_offset = 7
    assert printer_state == expected_state
    printer_state.execute_command(['G92'])
    expected_state.current_position = [0,0,0]
    expected_state.origin_offset = [30,5,0]
    assert printer_state == expected_state

def test_M17():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M17 command
    printer_state.execute_command(['M17'])
    assert printer_state == expected_state

def test_M73():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M73 command
    printer_state.execute_command(['M73'])
    assert printer_state == expected_state

def test_M77():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M77 command
    printer_state.execute_command(['M77'])
    assert printer_state == expected_state

def test_M83():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M83 command
    printer_state.execute_command(['M83'])
    assert printer_state == expected_state

def test_M84():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M84 command
    printer_state.execute_command(['M84'])
    assert printer_state == expected_state

def test_M104():
    # Also test M104.1?!
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M104 command
    printer_state.execute_command(['M104'])
    assert printer_state == expected_state

def test_M106():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M106 command
    printer_state.execute_command(['M106'])
    assert printer_state == expected_state

def test_M107():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M107 command
    printer_state.execute_command(['M107'])
    assert printer_state == expected_state

def test_M109():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M109 command
    printer_state.execute_command(['M109'])
    assert printer_state == expected_state

def test_M115():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M115 command
    printer_state.execute_command(['M115'])
    assert printer_state == expected_state

def test_M140():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M140 command
    printer_state.execute_command(['M140'])
    assert printer_state == expected_state

def test_M142():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M142 command
    printer_state.execute_command(['M142'])
    assert printer_state == expected_state

def test_M190():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M190 command
    printer_state.execute_command(['M190'])
    assert printer_state == expected_state

def test_M201():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M201 command
    printer_state.execute_command(['M201'])
    assert printer_state == expected_state

def test_M203():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M203 command
    printer_state.execute_command(['M203'])
    assert printer_state == expected_state

def test_M204():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M204 command
    printer_state.execute_command(['M204'])
    assert printer_state == expected_state

def test_M205():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M205 command
    printer_state.execute_command(['M205'])
    assert printer_state == expected_state

def test_M217():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M217 command
    printer_state.execute_command(['M217'])
    assert printer_state == expected_state

def test_M220():
    printer_state = PrinterState()
    expected_state = PrinterState()
    #TODO: Implement M220 command
    printer_state.execute_command(['M220'])
    assert printer_state == expected_state

def test_M221():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M221 command
    printer_state.execute_command(['M221'])
    assert printer_state == expected_state

def test_M302():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M302 command
    printer_state.execute_command(['M302'])
    assert printer_state == expected_state

def test_M486():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M486 command
    printer_state.execute_command(['M486'])
    assert printer_state == expected_state

def test_M555():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M555 command
    printer_state.execute_command(['M555'])
    assert printer_state == expected_state

def test_M862_1():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M862.1 command
    printer_state.execute_command(['M862.1'])
    assert printer_state == expected_state

def test_M862_3():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M862.3 command
    printer_state.execute_command(['M862.3'])
    assert printer_state == expected_state

def test_M900():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement M900 command
    printer_state.execute_command(['M900'])
    assert printer_state == expected_state

def test_P0():
    # e.g. P0 S1 L1 D0; park the tool
    # e.g. P0 S1 ; park tool
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement P0 command
    printer_state.execute_command(['T0'])
    assert printer_state.selected_tool == 0
    printer_state.execute_command(['P0'])
    assert printer_state == expected_state

def test_T0():
    printer_state = PrinterState()
    expected_state = PrinterState()
    # TODO: Implement T0 command
    printer_state.execute_command(['T0'])
    expected_state.selected_tool = 0
    printer_state.execute_command(['T3', 'S1', 'L0', 'D0'])
    expected_state.selected_tool = 3
    assert printer_state == expected_state

def test_multiple_states():
    gcode = GCode(gcode_str)
    assert gcode.lines[0].state.current_position == [0,0,22]
    assert gcode.lines[6].state.current_position == [135.599,58.092,22]
    assert gcode.lines[7].state.current_position == [138.898,61.391,22]

def test_full_sanity_check():
    gcode = GCode.from_file('tests/gcode/multi.gcode')
    assert gcode.line_count == 294548
    assert gcode.lines[-1].state.layer_height == 72.2
    assert gcode.lines[-1].state.layer == 361
    assert gcode.lines[14850].state.print_move_type == "External perimeter"


# def test_lineparse():
#     printer_state = PrinterState()
#     expected_state = PrinterState()
#     assert GCode().parse_line('    ', printer_state) == ('    ', printer_state)
#     assert GCode().parse_line(';this is a comment', printer_state) == (';this is a comment', printer_state)
#     expected_state.current_position = (135.599, 58.092, 0)
#     assert GCode().parse_line('G1 X135.599 Y58.092 E.0677', printer_state) == ('G1 X135.599 Y58.092 E.0677', printer_state)

## lower case test

# comapre extrusion amount to expected from Prusa slicer