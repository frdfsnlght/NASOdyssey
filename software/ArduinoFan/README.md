This folder contains the source for the embedded Arduino microcontroller on the Odyssey X86J4125864.

The microcontroller controlls a system fan mainly for cooling the hard drives. The fan is a 5V fan and
can be of the PWM (4 pin) or non-PWM (3 pin) variety. In my design, there is a small PCB plugged into
the Arduino header and the fan plugs into this board. See the PCB design for more information.

## Configuration

The sketch can be configured by changing the constants at the top of the file. The interesting options are these:

```
const bool PWM = true;
```
Does the fan support PWM? This should be true even of the fan isn't a PWM fan (4 pin) and you want to use
PWM on the power pin (this may not work for all fans).

```
const bool POWER_INVERTED = false;
```
Should the power pin output be inverted? When set to false, the power pin will be set HIGH to supply power to the fan.

```
const bool PWM_INVERTED = false;
```
Should the PWM pin output be inverted? When set to false, the PWM pin will be set HIGH when at 100% dutycycle.

```
const bool PWM_ON_POWER = false;
```
This should be true if you're using a non-PWM (3 pin) fan but want to controll it's speed using PWM. When this is true,
the PWM signal will be output on the power pin instead of the PWM pin. This may not work for all fans.

```
const int POWER_PIN = 11;
const int SENSE_PIN = 12;
const int PWM_PIN = 13;
```
These are the IO pins to use for the various signals. If you connect your fan differently, you may need to change these.

## Building

The build.sh script assumes the arduino-cli command is in the path and will use it to compile, then upload the
sketch. Setting up arduino-cli for the Odyssey X86J4125864 is detailed below.

## Use

With the sketch is running, you can connect to the **/dev/ttyACM0** serial port at 115000bps using a terminal emulator like
**python -m serial.tools.miniterm /dev/ttyACM0 115000**. There's currently only one command:

```
DUTYCYCLE <n>
```

Where `<n>` should be a number from 0 to 100 inclusive. Keep in mind most PWM fans don't work under 20% dutycycle. If you're not using PWM (PWM = false), any number
over 0 will turn the fan on and 0 turns it off.

Whenever the fan speed changes, the RPM will be reported by a **RPM <rpm>** line at about a 1 second interval.

## arduino-cli

See the [arduino-cli documentation](https://arduino.github.io/arduino-cli/latest/) for reference.

For my build using OpenMediaVault as my OS, these are the steps I took to install and configure arduino-cli:

1. Download the latest release for 64 bit Linux from [this page](https://github.com/arduino/arduino-cli/releases).
2. In the root user's home directory, create a "bin" sub directory.
3. Unpack the download from step 1 and put the arduino-cli executable in the new bin directory. Make sure it's executable.
4. Add the new bin directory to the path.
5. Run **arduino-cli config init** which will create a configuration file at the indicated path.
6. Edit the configuration file and add **https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json** under **board_manager -> additional_urls**.
7. Run **arduino-cli core update-index** which will download the new board indexes.
8. Run **arduino-cli core install Seeeduino:samd** to install the appropriate cores and tools.

Assuming you didn't receive any errors, you should be ready to compile and upload.

