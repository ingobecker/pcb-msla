from pkg_resources import resource_filename

import click
import yaml

from pcb_msla import Converter

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
    c.exp_test()
