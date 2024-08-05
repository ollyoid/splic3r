import re

class DrillFile:
    
    def __init__(self, raw_file):
        self.raw_file = raw_file
        self.tools = []
        self.selected_tool = None
        self.drills = {}
        self.parse()

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as f:
            return cls(f.read())
        
    def parse(self):
        for line in self.raw_file.split('\n'):
            if line.startswith('T'):
                self.parse_tool(line)
            elif line.startswith('X'):
                self.parse_drill(line)
    
    def parse_tool(self, line):
        pattern = re.compile(r'(T\d+)C(\d+.?\d*)')
        if match := pattern.match(line):
            tool = match.group(1)
            tool_size = float(match.group(2))
            self.tools.append((tool, tool_size))
            self.drills[tool] = []
            self.selected_tool = tool
        if match := re.match(r'(T\d+)', line):
            self.selected_tool = match.group(1)


    def parse_drill(self, line):
        x, y = line[1:].split('Y')
        self.drills[self.selected_tool].append((float(x), float(y)))
        
    