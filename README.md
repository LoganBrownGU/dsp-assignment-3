# DSP Assignment 3
Send data wirelessly using a laser and an LDR.

## Concept
Modulate a laser using binary ASK, and detect the signal using a light dependent resistor placed in the beam. 

Set the LDR up in a voltage divider, and measure the voltage across the LDR using an analogue input on the MCU.

## Frequency 

The LDR will not be able to react to frequencies higher than around 50 Hz. As such, a keying frequency of approx. 25 Hz would be suitable - this will preserve some harmonics of the square wave.