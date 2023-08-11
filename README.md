# Measuring the water level of my coffee machine

Using micropython on the pico + ultrasonic sensor HC-SR04.
Make sure that the GPIO's operate (input and output) only at 3.3V and the sensor at 5.

Therefore, I use a logic shifter (3V -> 5V) for the trigger (pin of the sensor) and 2 resistors with 10kOhm and 22kOhm to downsize 5V -> 3.4 -> GND.
These resistors are positioned in chain, the output of the sensor is going through 10kOhm followed by 22kOhm. After the first one, I can connect my pico input pin to.

## MicroPico

Usefull VS Code extension to manage development with the pico.

## Auto run

Just name the file main.py and upload it/ the project to the pico. Close VS Code or at least the extension MicroPico, because it blocks the bootup otherwise.

## Files

Currently, `ultrasonic_sensor.py` is the only working example, using plain (Micro)Python. I plan to use the programmable I/O (PIO) functionality from the pico to handle the sensor trigger/ echo signals in the future.
