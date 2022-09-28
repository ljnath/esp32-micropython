"""
MIT License

Copyright (c) 2022 ljnath

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Micropython code to generate and display random number on a 7-segment common cathode LED display.
Tested this code on ESP32

Author: Lakhya Jyoti Nath
Date: September 2022

7segment LED display

        A
    o--------o
    |        | B
  F |   G    |
    o--------o
    |        | C
  E |        |
    o--------o
        D

"""

import random
import time

import machine

TIMEOUT = 60    # timeout in seconds to auto-stop the script

A = machine.Pin(25, machine.Pin.OUT)    # GPIO25
B = machine.Pin(26, machine.Pin.OUT)    # GPIO26
C = machine.Pin(16, machine.Pin.OUT)    # GPIO16
D = machine.Pin(17, machine.Pin.OUT)    # GPIO17
E = machine.Pin(18, machine.Pin.OUT)    # GPIO18
F = machine.Pin(32, machine.Pin.OUT)   	# GPIO32
G = machine.Pin(33, machine.Pin.OUT)   	# GPIO33

ALL_SEGMENTS = (A, B, C, D, E, F, G)

DIGITS = {
    0: (A, B, C, D, E, F),
    1: (B, C),
    2: (A, B,  D, E, G),
    3: (A, B, C, D, G),
    4: (B, C, F, G),
    5: (A, C, D, F, G),
    6: (A, C, D, E, F, G),
    7: (A, B, C),
    8: (A, B, C, D, E, F, G),
    9: (A, B, C, D, F, G)
}


def clear_display():
    """
    Function to clear the display. It will basically turn-off all the segments in the LED display
    """
    _ = [segment.off() for segment in ALL_SEGMENTS]


def get_end_time():
    """
    Function to generate end time for this script.
    At the end-time, the script will auto-exit, this is to avoid infinte script execution
    """
    start_time = time.ticks_ms()
    end_time = start_time + (TIMEOUT * 1000)
    print(f'Start time = {start_time} ms; end time = {end_time}')
    return end_time


def display_number(number: int, blink_count: int):
    """
    Function to display a number on the 7-segment LED display
    :param number : number which needs to be displayed
    :param blink_count : number of times the number should blink before showing a new number
    """
    segments_to_lit = DIGITS[number]

    while blink_count > 0:
        time.sleep(0.5)
        clear_display()
        time.sleep(0.5)
        _ = [segment.on() for segment in segments_to_lit]
        blink_count -= 1


def blink_random_digit():
    """
    Main function for random number generation and triggering the display
    """
    clear_display()
    end_time = get_end_time()

    while True:
        random_digit = random.randint(0, 9)
        display_number(random_digit, 2)

        if time.ticks_ms() > end_time:
            print('Timeout reached !')
            break


if __name__ == '__main__':
    blink_random_digit()
