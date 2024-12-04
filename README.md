# DSP Assignment 3
Send data wirelessly using a laser and an LDR.

## Concept
Modulate a laser using binary ASK (or maybe FSK), and detect the signal using a photodiode placed in the beam. 

Set the LDR up in a voltage divider, and measure the voltage across the resistor using an analogue input on the MCU.

## Frequency 

Potodiodes are quite responsive, so the frequency is mostly limited by the max sampling rate of the ADC: 1000 Hz. 
