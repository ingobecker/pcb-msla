from pkg_resources import resource_filename

import click
import yaml

from pcb_msla import Converter
from pcb_msla import GCode

@click.group()
@click.option('-d', '--device',
                type=click.Choice(['elegoo-mars', 'photon']),
                default='elegoo-mars',
                show_default=True,
                help='Choose your 3D printer.')
@click.pass_context
def cli(ctx, device):

    devices_cfg_path = resource_filename('pcb_msla', 'data/devices.yml')
    with open(devices_cfg_path) as f:
        devices_cfg = yaml.load(f, Loader=yaml.Loader)

    ctx.obj = devices_cfg['devices'][device]

@cli.command()
@click.option('-e', '--exposure',
                default=Converter.DEFAULT_EXPOSURE_TIME,
                show_default=True,
                help='Exposuretime in seconds')
@click.argument('infile', type=click.Path(exists=True))
@click.argument('outfile')
@click.pass_obj
def convert(device_cfg, exposure, infile, outfile):
    """Convert a gerber file into a cbddlp/photon file.
    
    INFILE is a .gbr file. A file with the same basename but the extension .drl is
    loaded automatically if exists.

    OUTFILE is a .cbddlp or .photon file depending on the choosen device.
    """

    c = Converter(device_cfg, output=outfile)
    c.load_input(gbr=infile)
    c.exposure_time = exposure
    c.render()
    print("Creating {}...".format(outfile))
    print("PCB dimensions: {} x {} mm".format(c.pcb_width_mm, c.pcb_height_mm))
    c.render_blank()

@cli.command()
@click.argument('offset')
@click.pass_obj
def gcode(device_cfg, offset):
    """Generate g-code configs for PCB exposure.

    Use this command to generate g-code files which make your printer
    behave more suitable for PCB exposure. It disables the normal peeling motion
    and respects your PCBs thickness as well as the thickness of the padding
    material.

    To determine the OFFSET, extend the homing sensor by taping a piece of paper
    of a length of around 15 mm to it. Select the printers menu for manual
    positioning and home the printer. The buildplate should stop around 15 mm
    higher than normaly. Put your PCB and the padding material under the
    buildplate and lower the buildplate in increments of 1 mm until the PCB
    can't be moved by hand easily. This number is the offset needed by
    this command.

    ¡WARNING!

    DO THIS AT YOUR OWN RISK. MAKE SURE THE PIECE OF PAPER DOES NOT
    FALL OFF. OTHERWISE THE PRINTER MIGHT CRUSH YOUR PRINTERS DISPLAY!

    Generated files:

    setup.gcode - Enable "PCB mode".

    cleanup.gcode -  Disable "PCB mode" and restore the printers normal
    operation.
    """
    print("Creating g-code files...")
    gcode = GCode(offset)
    gcode.render()

@cli.command()
@click.option('--start',
                default=6 * 60,
                show_default=True,
                help='Start test series at --start seconds.')
@click.option('--steps',
                default=4,
                show_default=True,
                help='Number of exposure steps.')
@click.option('--interval',
                default=60,
                show_default=True,
                help='Seconds each exposure step should take.')
@click.option('--test-pattern',
                default='built-in',
                show_default=True,
                help='Path to custom test-pattern')
@click.argument('outfile')
@click.pass_obj
def test(device_cfg, start, steps, interval, test_pattern, outfile):
    """Generate an exposure test series.

    An exposure test series is created which displays a test pattern STEPS times.
    Each INTERVAL seconds the number of patterns displayed is decremented by
    one. START determines the minimum exposure time in seconds used for the
    exposure series whereas START + STEPS * INTERVAL is the maximum exposure time.
    By default, a built-in pattern with the most common trace widths and drill
    diameters used by THT hobbyists is used.
    """
    if test_pattern == 'built-in':
        infile = None

    c = Converter(device_cfg, output=outfile)
    c.load_test_input(gbr=infile)
    c.exp_test_start = start
    c.exp_test_samples = steps
    c.exp_test_interval = interval
    c.exp_test()

    print("Creating {}...".format(outfile))
    print("PCB dimensions: {} x {} mm".format(c.pcb_width_mm, c.pcb_height_mm))
    c.render_blank()
