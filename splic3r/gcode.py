import re
from copy import deepcopy

class GCode:
    def __init__(self, raw_data=""):
        self.raw_data = raw_data
        self.lines = []
        self.deconstruct()

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as file:
            raw_data = file.read()
        return cls(raw_data)
    

    def deconstruct(self):
        lines = self.raw_data.splitlines()
        current_state = PrinterState()
        for line in lines:
            self.lines.append(self.parse_line(line, current_state))
        self.line_count = len(self.lines)

    def parse_line(self, line, current_state):
        if line.lstrip().startswith(';'):
            return GcodeLine(line, deepcopy(current_state.interpret_comment(line)))
        elif line.lstrip() == '':
            return GcodeLine(line, current_state)
        else:
            parts = self.split_command(line)
            return GcodeLine(line, deepcopy(current_state.execute_command(parts)))

    def split_command(self, line):
        line = line.split(';')[0] # Remove comments	
        pattern = r'([GMTDP]\d+\.?\d*|T\d+|[XYZABCEFHIJRS]-?\d*\.?\d*)'
        matches = re.findall(pattern, line)

        return matches

class GcodeLine():
    def __init__(self, line, state):
        self.line = line
        self.state = state

class PrinterState:
    def __init__(self):
        self.current_position = [0,0,0]
        self.hotend_temperature = []
        self.extruding = False
        self.bed_temperature = 0
        self.fan_speed = 0
        self.selected_tool = None
        self.amount_extruded = 0
        self.feedrate = 0
        self.relative = False # Absolute by default according to reprap
        self.origin_offset = [0,0,0]
        self.extrude_offset = 0
        self.layer = 0
        self.layer_height = 0
        self.mode = None
        self.print_move_type = None
        self.mode = None
        self.var_dict = {}

    def interpret_comment(self, comment):
        self.extruding = False
        pattern = r'\s*;\s*([\w\s]+)\s*=\s*(.*)'
        match = re.match(pattern, comment)
        if match:
            self.var_dict[match.group(1).strip()] = match.group(2).strip()
        elif comment.startswith(';LAYER_CHANGE'):
            self.layer += 1
        elif comment.startswith(';Z:'):
            self.layer_height = float(comment.split(':')[1])
        elif comment.startswith('; CP TOOLCHANGE START'):
            self.mode = 'tool_change'
        elif comment.startswith('; CP TOOLCHANGE UNLOAD'):
            self.mode = 'tool_unload'
        elif comment.startswith('; CP TOOLCHANGE WIPE'):
            self.mode = 'tool_wipe'
        elif comment.startswith('; CP TOOLCHANGE END'):
            self.mode = None
        elif comment.startswith(';TYPE:'):
            self.print_move_type = comment.split(':')[1]
        
        return self                              
        

    def execute_command(self, command):
        self.extruding = False
        if command[0] == 'G0':
            self.G1(command[1:])
        elif command[0] == 'G1':
            self.G1(command[1:])
        elif command[0] == 'G2':
            self.G2(command[1:])
        elif command[0] == 'G3':
            self.G2(command[1:])
        elif command[0] == 'G4':
            self.G4(command[1:])
        elif command[0] == 'G20':
            self.G20(command[1:])
        elif command[0] == 'G21':
            self.G21(command[1:])
        elif command[0] == 'G28':
            self.G28(command[1:])
        elif command[0] == 'G29':
            self.G29(command[1:])
        elif command[0] == 'G90':
            self.G90(command[1:])
        elif command[0] == 'G92':
            self.G92(command[1:])
        elif command[0] == 'M17':
            self.M17(command[1:])
        elif command[0] == 'M73':
            self.M73(command[1:])
        elif command[0] == 'M77':
            self.M77(command[1:])
        elif command[0] == 'M83':
            self.M83(command[1:])
        elif command[0] == 'M84':
            self.M84(command[1:])
        elif command[0] == 'M104':
            self.M104(command[1:])
        elif command[0] == 'M104.1':
            self.M104(command[1:])
        elif command[0] == 'M106':
            self.M106(command[1:])
        elif command[0] == 'M107':
            self.M107(command[1:])
        elif command[0] == 'M109':
            self.M109(command[1:])
        elif command[0] == 'M115':
            self.M115(command[1:])
        elif command[0] == 'M140':
            self.M140(command[1:])
        elif command[0] == 'M142':
            self.M142(command[1:])
        elif command[0] == 'M190':
            self.M190(command[1:])
        elif command[0] == 'M201':
            self.M201(command[1:])
        elif command[0] == 'M203':
            self.M203(command[1:])
        elif command[0] == 'M204':
            self.M204(command[1:])
        elif command[0] == 'M205':
            self.M205(command[1:])
        elif command[0] == 'M217':
            self.M217(command[1:])
        elif command[0] == 'M220':
            self.M220(command[1:])
        elif command[0] == 'M221':
            self.M221(command[1:])
        elif command[0] == 'M302':
            self.M302(command[1:])
        elif command[0] == 'M486':
            self.M486(command[1:])
        elif command[0] == 'M555':
            self.M555(command[1:])
        elif command[0] == 'M862.1':
            self.M862_1(command[1:])
        elif command[0] == 'M862.3':
            self.M862_3(command[1:])
        elif command[0] == 'M900':
            self.M900(command[1:])
        elif command[0].startswith('P'):
            self.P(command)
        elif command[0].startswith('T'):
            self.T(command)
        else:
            raise NotImplementedError(f"Command {command[0]} not implemented")
        return self

    # G1: Linear move
    def G1(self, args):
        for arg in args:
            if arg.startswith('X'):
                if self.relative:
                    self.current_position[0] += float(arg[1:])
                else: 
                    self.current_position[0] = float(arg[1:])
            elif arg.startswith('Y'):
                if self.relative:
                    self.current_position[1] += float(arg[1:])
                else: 
                    self.current_position[1] = float(arg[1:])
            elif arg.startswith('Z'):
                if self.relative:
                    self.current_position[2] += float(arg[1:])
                else: 
                    self.current_position[2] = float(arg[1:])
            elif arg.startswith('E'):
                self.extruding = True
                self.amount_extruded += float(arg[1:])
            elif arg.startswith('F'):
                self.feedrate = float(arg[1:])
            else:
                print(f"G1 Argument {arg} not recognized")   
    
    # G2: Clockwise arc
    def G2(self, args):
        # Since we aren't keeping track of intermediary points, we only need to know about start and end points
        # We can treat this the same as G0 and G1
        args = [arg for arg in args if not arg.startswith('I') and not arg.startswith('J') and not arg.startswith('R')]
        ## Confirm that both X and Y coordinates are supplied
        assert any(arg.startswith('X') for arg in args) and any(arg.startswith('Y') for arg in args), "Both X and Y coordinates must be supplied"
        self.G1(args)

    ## G4: Dwell - Nothing to do, we're not counting time or anything yet
    def G4(self, args):
        for arg in args:
            if arg.startswith('P'):
                pass
            elif arg.startswith('S'):
                pass
            else:
                print(f"G4 Argument {arg} not recognized")

    def G20(self, args):
        raise NotImplementedError("G20 'Set units to inches' not implemented")
    
    def G21(self, args):
        pass # Assuming we are already in mm mode

    # G28: Home
    def G28(self, args):
        for arg in args:
            if arg.startswith('X'):
                self.current_position[0] = 0
            elif arg.startswith('Y'):
                self.current_position[1] = 0
            elif arg.startswith('Z'):
                self.current_position[2] = 0
            elif arg.startswith('W'):
                pass
            elif arg.startswith('C'):
                pass
            elif arg.startswith('P'):
                pass
            elif arg.startswith('I'):
                pass
            else:
                print(f"G28 Argument {arg} not recognized")
        ## if none start with x, y, or z, then home all axes
        if not any(arg.startswith('X') or arg.startswith('Y') or arg.startswith('Z') for arg in args):
            self.current_position = [0,0,0]

    # G29: Auto bed leveling
    def G29(self, args):
        pass #TODO: Implement G29 command

    # G90: Absolute positioning
    def G90(self, args):
        self.relative = False
    
    # G91: Relative positioning
    def G91(self, args):
        self.relative = True

    # G92: Set position
    def G92(self, args):
        for arg in args:
            val =  0 if arg[1:] == "" else float(arg[1:])
            if arg.startswith('X'):
                self.origin_offset[0] += self.current_position[0] - val
                self.current_position[0] = val
            elif arg.startswith('Y'):
                self.origin_offset[1] += self.current_position[1] - val
                self.current_position[1] = val
            elif arg.startswith('Z'):
                self.origin_offset[2] += self.current_position[2] - val
                self.current_position[2] = val
            elif arg.startswith('E'):
                self.extrude_offset += self.amount_extruded - val
                self.amount_extruded = val
        if len(args) == 0:
            self.origin_offset = [x +y for x,y in zip(self.current_position, self.origin_offset)]
            self.extrude_offset += self.amount_extruded
            self.current_position = [0,0,0]
            self.amount_extruded = 0

    # M17: Enable/Power all stepper motors
    def M17(self, args):
        pass  # TODO: Implement M17 command

    # M73: Set build percentage
    def M73(self, args):
        pass  # TODO: Implement M73 command

    # M77: Disable/Power down all stepper motors
    def M77(self, args):
        pass  # TODO: Implement M77 command

    # M83: Set extruder to relative mode
    def M83(self, args):
        pass  # TODO: Implement M83 command

    # M84: Stop idle hold
    def M84(self, args):
        pass  # TODO: Implement M84 command

    # M104: Set extruder temperature
    def M104(self, args):
        pass  # TODO: Implement M104 command

    # M106: Set fan speed
    def M106(self, args):
        pass  # TODO: Implement M106 command

    # M107: Turn off fan
    def M107(self, args):
        pass  # TODO: Implement M107 command

    # M109: Set extruder temperature and wait
    def M109(self, args):
        pass  # TODO: Implement M109 command

    # M115: Get firmware version and capabilities
    def M115(self, args):
        pass  # TODO: Implement M115 command

    # M140: Set bed temperature
    def M140(self, args):
        pass  # TODO: Implement M140 command

    # M142: Set humidity
    def M142(self, args):
        pass  # TODO: Implement M142 command

    # M190: Set bed temperature and wait
    def M190(self, args):
        pass  # TODO: Implement M190 command

    # M201: Set maximum acceleration
    def M201(self, args):
        pass  # TODO: Implement M201 command

    # M203: Set maximum feedrate
    def M203(self, args):
        pass  # TODO: Implement M203 command

    # M204: Set default acceleration
    def M204(self, args):
        pass  # TODO: Implement M204 command

    # M205: Set advanced settings
    def M205(self, args):
        pass  # TODO: Implement M205 command

    # M217: Set filament diameter
    def M217(self, args):
        pass  # TODO: Implement M217 command

    # M220: Set speed factor override percentage
    def M220(self, args):
        pass  # TODO: Implement M220 command

    # M221: Set flow rate
    def M221(self, args):
        pass  # TODO: Implement M221 command

    # M302: Allow cold extrusion
    def M302(self, args):
        pass  # TODO: Implement M302 command

    # M486: Set print progress
    def M486(self, args):
        pass  # TODO: Implement M486 command

    # M555: Set firmware type
    def M555(self, args):
        pass  # TODO: Implement M555 command

    # M862.1: Check nozzle diameter
    def M862_1(self, args):
        pass  # TODO: Implement M862.1 command

    # M862.3: Check Model Name
    def M862_3(self, args):
        pass  # TODO: Implement M862.3 command

    # M900: Set linear advance
    def M900(self, args):
        pass  # TODO: Implement M900 command

    # T: Select tool
    def P(self, args):
        assert int(args[0][1:]) == 0 or int(args[0][1:]) == self.selected_tool or self.selected_tool == None , "Tool change must be to the same tool"
        self.selected_tool = None
        for arg in args[1:]:
            if arg.startswith('F'):
                pass
            elif arg.startswith('S1'):
                # S1: Don't move the tool in XY after change
                # TODO: Understand behaviour
                pass
            elif arg.startswith('M'):
                # M0/1: Use tool mapping or not (default is yes)
                pass
            elif arg.startswith('L'):
                # Lx: Z Lift settings 0 =- no lift, 1 = lift by max MBL diff, 2 = full lift(default)
                pass
            elif arg.startswith('D'):
                # Dx 0 = do not return in Z after lift, 1 = normal return
                pass
            else:
                print(f"T Argument {arg} not recognized")

    # T: Select tool
    def T(self, args):
        self.selected_tool = int(args[0][1:])
        for arg in args[1:]:
            if arg.startswith('F'):
                pass
            elif arg.startswith('S1'):
                # S1: Don't move the tool in XY after change
                # TODO: Understand behaviour
                pass
            elif arg.startswith('M'):
                # M0/1: Use tool mapping or not (default is yes)
                pass
            elif arg.startswith('L'):
                # Lx: Z Lift settings 0 =- no lift, 1 = lift by max MBL diff, 2 = full lift(default)
                pass
            elif arg.startswith('D'):
                # Dx 0 = do not return in Z after lift, 1 = normal return
                pass
            else:
                print(f"T Argument {arg} not recognized")

    
        

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
        
    