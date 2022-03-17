This folder contains the source for the embedded Arduino microcontroller on the Odyssey X86J4125864.

The microcontroller controls a system fan mainly for cooling the hard drives. The fan is a 5V fan and
can be of the PWM (4 pin) or non-PWM (3 pin) variety. In my design, there is a small PCB plugged into
the Arduino header and the fan plugs into this board. See the PCB design for more information.

## Configuration

The sketch can be configured by changing the constants at the top of the file. The interesting options are these:

```
const bool POWER_INVERTED = false;
```
Should the power pin output be inverted? When set to false, the power pin will be set HIGH to supply power to the fan.

```
const bool PWM_INVERTED = false;
```
Should the PWM pin output be inverted? When set to false, the PWM pin will be set HIGH when at 100% dutycycle.

```
const int POWER_PIN = 5;
const int SENSE_PIN = 6;
const int PWM_PIN = 7;
```
These are the IO pins to use for the various signals. If you connect your fan differently, you may need to change these.
**NOTE:** If you want to use a different pin for the PWM signal, you can't simply change PWM_PIN. The PWM signalling used
in the code is at a much lower level than the standard analogWrite Arduino function due to the high frequency required
by computer fans. See the source code for more information.

## Building

The build.sh script assumes the arduino-cli command is in the path and will use it to compile, then upload the
sketch. Setting up arduino-cli for the Odyssey X86J4125864 is detailed below.

## Use

With the sketch is running, you can connect to the **/dev/ttyACM0** serial port at 9600 bps using a terminal emulator like
**python -m serial.tools.miniterm /dev/ttyACM0**. These are the available commands:

```
RPM
```
Returns the current RPM speed of the fan in the form **RPM <rpm>** where `<rpm>` is an integer.

```
DUTYCYCLE
```
Returns the current dutycycle of the PWM signal in the form **DUTYCYCLE x** where "x" is an integer.

```
DUTYCYCLE <dc>
```
Sets the dutycycle of the PWM signal where `<dc>` should be a number from 0 to 100 inclusive. Keep in mind most PWM fans don't work
under 20% dutycycle. If you're not using a PWM fan, any number over 0 will turn the fan on and 0 turns it off.
After setting the dutycycle, a response of **OK** will be returned.

Whenever the fan speed changes, the RPM will be reported by a **RPM <rpm>** line at most once a second.

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

