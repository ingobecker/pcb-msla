from string import Template
# elegoo factory home in mm: 47
class GCode(object):

    GCODE_SETUP =   "M8489 P3\n" \
                    "M8070 Z0\n" \
                    "M8070 S0\n" \
                    "M8083 I1\n" \
                    "M8084 Z${offset}\n" \
                    "M8500\n" \

    GCODE_CLEANUP = "M8489 P3\n"\
                    "M8070 Z6\n" \
                    "M8070 S3\n" \
                    "M8083 I1\n" \
                    "M8084 Z0\n" \
                    "M8500\n" \
                    "G28 Z"

    GCODE_FILES   = {
            'setup.gcode': GCODE_SETUP,
            'cleanup.gcode': GCODE_CLEANUP
            }

    def __init__(self, offset):
        self.offset = offset

    def render(self):
        for filename, gcode in self.GCODE_FILES.items():
            gcode_rendered = Template(gcode).substitute(offset = self.offset)
            with open(filename, 'w+') as f:
                f.write(gcode_rendered)
