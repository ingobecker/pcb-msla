# pcb-msla

Expose PCBs on your Elegoo Mars, Anycubic photon or any compatible 3D printer using standard gerber files. `pcb-msla` can convert standard `.gbr`/`.drl` files into `.cbddlp`/`.photon` files. 

It also features an exposure series function which helps to determine the correct exposure time for your 3D printer in a single pass.

## Features

* **Exposure test series** function to determine the correct exposure time in a single pass.
* **Setup PCB-Mode** use the buildplate to hold PCBs in place during exposure.
* **Convert gerber into cbddlp** to use them directly on your elegoo mars.

## Getting Started

Before installing, make sure you have installed python 3 as well as `cairo`. Proceed installing `pcb-msla` using pip:

```
$ pip install git+https://github.com/ingobecker/pcb-msla@master
```

You should now be able to invoke `pcb-msla` from the commandline.

## Enable PCB-Mode

The first thing to do is to setup **PCB-Mode** on your printer. That is what
the `gcode` subcommand is for. It generates a `.gcode` file to setup `PCB-Mode`
(`setup.gcode`) and second one to restore your printer back to normal operation mode(`cleanup.gcode`).

In PCB-Mode, your printer uses the buildplate to clamp down the PCB before it
starts the exposure. It also disables the peeling motion which in normal
operation mode seperates the printed layer from the FEP film. 

In order to clamp down a PCB correctly, the z-axis zero point has to be modified 
and the printer needs to know the exact distance from the buildplates new zero
point to the upper side of the PCB when placed onto the printers LCD.

To offset the zeropoint upwards, use some tape to attach a little strip of
paper to the metal part that reaches into the photo interruptor of the printer.
The paper strip should be around 15 mm.  With the paper attached open the
printers menu for manual positioning home the printer. It should home the
buildplate about the length of the attached paperstrip above the printers LCD.

Place a PCB and some padding material in between the buildplate and the display.
Lower the buildplate in increments of 1 mm until the PCB is clamped down
firmly. The number of millimeters is the offset you will need for the `pcb-msla
gcode <OFFSET>` command.

Copy the generated `.gcode` files to a usb drive and connect it to your printer.
Select the `setup.gcode` file. The printer is now operating in PCB-Mode.


## Exposure Series Test

If you are using your 3D printer for the first time with `pcb-msla` or you have
changed the type of photoresist PCB you have to determine the correct exposure
time first. With the help of `pcb-msla test` you can generate a exposure test
series pattern. With this feature, you cant test different exposure times in on
 run. To expose a test series with 4 different exposure times starting at 6 minutes
incrementing the the for each successive exposure by 60 seconds run the following
command:

```
$ pcb-msla test --start 360 --steps 4 --interval 60 test.cbddlp
```

For more details run:

```
$ pcb-msla test --help
```

## Convert Gerber file

Converting a `.gbr` file into a `.cbddlp` file is simple. Run the following for an
exposure time of 9 minutes:

```
$ pcb-msla convert -e 540 input.gbr output.cbddlp
```

## Blank?

Every generated `<OUTPUT_NAME>.cbddlp`-File is accompanied by a file ending
with `<OUTPUT_NAME>_blank.cdbdlp`. This file will expose an area with the size
of the bounding box of the actual PCB. It is useful to expose the remaining
photoresist on the traces after the etching process and removing it by giving
the PCB another bath in the developer.
