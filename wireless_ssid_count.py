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

Micropython code to scan for wireless SSID and display the number of results it found on 7-segment LED display (common cathode).
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

import time

import machine
import network


class LedDisplay:
    """
    LedDisplay class to handling all the interaction with the 7-segment LED display
    """

    def __init__(self) -> None:
        # all avilable segments in a 7-segment LCD display
        self.__all_segment = ('A', 'B', 'C', 'D', 'E', 'F', 'G')

        # GPIO pins for displaying the TENS digit
        self.__tens_pins = (25, 26, 16, 17, 18, 32, 33)

        # GPIO pins for displaying the ONES digit
        self.__ones_pins = (27, 14, 23, 22, 1, 12, 13)

        # all possible digits
        self.__digits = {
            0: ('A', 'B', 'C', 'D', 'E', 'F'),
            1: ('B', 'C'),
            2: ('A', 'B', 'D', 'E', 'G'),
            3: ('A', 'B', 'C', 'D', 'G'),
            4: ('B', 'C', 'F', 'G'),
            5: ('A', 'C', 'D', 'F', 'G'),
            6: ('A', 'C', 'D', 'E', 'F', 'G'),
            7: ('A', 'B', 'C'),
            8: ('A', 'B', 'C', 'D', 'E', 'F', 'G'),
            9: ('A', 'B', 'C', 'D', 'F', 'G')
        }

    def __get_segments(self, position: str, digit: int = 8) -> tuple:
        """
        Method to get the segment responsible to display a digit.
        :param position : String value (ones or tens) which determine for which position the digit is for.
                          Based on this the pins will vary
        :param digit : Integer value, this is the digit for which the segement needs to be determined.
                       The default digit is considered as 8, where all the segment will be either ON (to display 8) or OFF (to clear display)
        """
        current_set_of_pins = ()

        # determining the pins-set based on the digit position, as we are using 2 LCD display,
        # the set of pins are different
        if position == 'ones':
            current_set_of_pins = self.__ones_pins
        elif position == 'tens':
            current_set_of_pins = self.__tens_pins

        # creating a dict of segments with key as A,B,C,D,E,F and G and value as instance of machine.Pin to interact with the Pin output value
        all_segments = {}
        for i in range(7):
            all_segments[self.__all_segment[i]] = machine.Pin(current_set_of_pins[i], machine.Pin.OUT)

        # casting and returning the segments applicable for given `digit`
        return tuple([value for key, value in all_segments.items() if key in self.__digits[digit]])

    def clear_display(self) -> None:
        """
        Method to clear both the ONES and TENS display
        """
        _ = [segment.off() for segment in self.__get_segments('ones')]
        _ = [segment.off() for segment in self.__get_segments('tens')]

    def show_number(self, number: int) -> None:
        """
        Method to show a 2 digit number on the LCD display
        :param number : Integer number to show
        """
        # displaying the ONES digit
        digit_at_ones_place = number % 10
        segments_to_lit = self.__get_segments('ones',  digit_at_ones_place)
        _ = [segment.on() for segment in segments_to_lit]

        if number > 9:
            digit_at_tens_place = number // 10
            segments_to_lit = self.__get_segments('tens',  digit_at_tens_place)
            _ = [segment.on() for segment in segments_to_lit]


class WirelessNetwork:
    """
    WirelessNetwork class for handling all wireless network operation
    """

    def __init__(self) -> None:
        print('Initializing wireless NIC')
        self.__nic = network.WLAN(network.STA_IF)
        self.__nic.active(True)                         # activating wireless network adapter

        self.__led_display = LedDisplay()

    def scan(self) -> list:
        """
        Method to scan for all available wirelesss SSIDs
        """
        return self.__nic.scan()


def main():
    """
    Driver function
    """
    led_display = LedDisplay()
    wireless_network = WirelessNetwork()

    while True:
        led_display.clear_display()
        available_ssids = wireless_network.scan()

        print(f'Number of SSID found: {len(available_ssids)}')
        led_display.show_number(len(available_ssids))

        print('Re-scanning again in 5 seconds...')
        time.sleep(5)


if __name__ == '__main__':
    main()
