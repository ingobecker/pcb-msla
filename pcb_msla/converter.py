import os
import os.path
import tempfile
from importlib import resources
from pkg_resources import resource_filename
from pathlib import Path

import cairo
from gerber.layers import load_layer
from gerber.render import RenderSettings, theme
from gerber.render.cairo_backend import GerberCairoContext
from pyphotonfile import Photon

class Converter(object):

    DEFAULT_OUTPUT = 'pcb.cbddlp'
    DEFAULT_EXPOSURE_TIME = 60 * 8
    PNG_OUTPUT = 'pcb.png'

    EXP_TEST_START = 6 * 60
    EXP_TEST_INTERVAL = 60
    EXP_TEST_SAMPLES = 4
    EXP_TEST_PATTERN = 'data/pattern.gbr'

    def __init__(self, device_cfg, output=None):

        self.device_cfg = device_cfg
        self.scale = self.device_cfg['size_px']['w'] / self.device_cfg['size_mm']['w']

        self.exp_test_start = self.EXP_TEST_START
        self.exp_test_interval = self.EXP_TEST_INTERVAL
        self.exp_test_samples = self.EXP_TEST_SAMPLES
        self.exp_test_tmp_dir = None

        self.exposure_time = self.DEFAULT_EXPOSURE_TIME

        self.gbr = None
        self.drl = None
        self.output = output
        if not output:
            self.output = self.DEFAULT_OUTPUT

        self.payload_ctx = GerberCairoContext(scale=self.scale)
        self.white = RenderSettings(color=theme.COLORS['white'])
        self.black = RenderSettings(color=theme.COLORS['black'])
        self.pcb_width = None
        self.pcb_height = None

    @property
    def pcb_width_mm(self):
        return self._px_to_mm(self.pcb_width)

    @property
    def pcb_height_mm(self):
        return self._px_to_mm(self.pcb_height)

    def _px_to_mm(self, px):
        return round(px / self.scale, 2)

    def load_test_input(self, gbr):
        if gbr == None:
            gbr = resource_filename('pcb_msla', self.EXP_TEST_PATTERN)
        self.load_input(gbr)
        
    def load_input(self, gbr, drl=None):
        if not drl:
            drl = "{}.drl".format(os.path.splitext(gbr)[0])
        self.traces_layer = load_layer(gbr)
        self.drills_layer = load_layer(drl)

    def _output_png_path(self):
        return self.PNG_OUTPUT

    def _exp_test_png_path(self, step):
        return "{}/{:05d}_{:02d}.png".format(self.exp_test_tmp_dir, step, 0)

    def _render_payload_surface(self):
        self.payload_ctx.render_layer(self.traces_layer, settings=self.black, bgsettings=self.white)
        self.payload_ctx.render_layer(self.drills_layer, settings=self.white)

    def _prepare_output_surface(self):
        self.ims = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                        self.device_cfg['size_px']['w'],
                        self.device_cfg['size_px']['h'])
        self.ic = cairo.Context(self.ims)
        self.ic.set_antialias(cairo.ANTIALIAS_NONE)
        self.ic.paint()

    def _render_output_surface(self):
        self._prepare_output_surface()
        self.ic.set_source_surface(self.payload_ctx.surface, 0, 0)
        self.ic.paint()
        self.ims.write_to_png(self._output_png_path())

    def _render_output_photon(self):
        p = Photon()
        p.bottom_layers = 1
        p.exposure_time_bottom = self.exposure_time
        p.delete_layers()
        p.append_layer(self._output_png_path())
        p.write(self.output)

    def render(self):
        self._render_payload_surface()
        self._render_output_surface()
        self._render_output_photon()
        self.pcb_width = self.payload_ctx.size_in_pixels[0]
        self.pcb_height = self.payload_ctx.size_in_pixels[1]

    def render_blank(self):
        self._prepare_output_surface()
        self.ic.set_source_rgb(1.0, 1.0, 1.0)
        self.ic.rectangle(0, 0, self.pcb_width, self.pcb_height)
        self.ic.fill()
        self.ims.write_to_png(self._output_png_path())
        output_split = os.path.splitext(self.output)
        self.output = "{}_blank{}".format(output_split[0], output_split[1])
        self._render_output_photon()

    def _render_exp_test_surface(self):
        self._prepare_output_surface()
        step_reversed = self.exp_test_samples
        for i in range(self.exp_test_samples):
             offset_y = self.payload_ctx.size_in_pixels[1] * i
             self.ic.set_source_surface(self.payload_ctx.surface, 0, offset_y)
             self.ic.paint()
             step_png = self._exp_test_png_path(step_reversed)
             self.ims.write_to_png(step_png)
             step_reversed = step_reversed - 1

    def exp_test(self):
        self._render_payload_surface()
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.exp_test_tmp_dir = tmp_dir
            self._render_exp_test_surface()
            p = Photon()
            p.bottom_layers = 1
            p.exposure_time_bottom = self.exp_test_start
            p.exposure_time = self.exp_test_interval
            p.delete_layers()
            p.append_layers(self.exp_test_tmp_dir)
 
            p.write(self.output)
        self.pcb_width = self.payload_ctx.size_in_pixels[0]
        self.pcb_height = self.payload_ctx.size_in_pixels[1] * self.exp_test_samples
        self.exposure_time = self.exp_test_start + (self.exp_test_samples *
                self.exp_test_interval)
