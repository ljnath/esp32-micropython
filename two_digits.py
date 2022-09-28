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

Micropython code to display 2 digits on to 2 7-segment LED display.
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


TIMEOUT = 300    # timeout in seconds to auto-stop the script


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

    def clear_display(self):
        """
        Method to clear both the ONES and TENS display
        """
        _ = [segment.off() for segment in self.__get_segments('ones')]
        _ = [segment.off() for segment in self.__get_segments('tens')]

    def show_number(self, number):
        """
        Method to show a 2 digit number on the LCD display
        """

        # displaying the ONES digit
        digit_at_ones_place = number % 10
        segments_to_lit = self.__get_segments('ones',  digit_at_ones_place)
        _ = [segment.on() for segment in segments_to_lit]

        if number > 9:
            digit_at_tens_place = number // 10
            segments_to_lit = self.__get_segments('tens',  digit_at_tens_place)
            _ = [segment.on() for segment in segments_to_lit]


def main():
    """
    Main function to display 2 digits number from 0 to 99
    """
    lcd_display = LedDisplay()
    lcd_display.clear_display()
    counter = 0

    while True:
        lcd_display.clear_display()         # clearing both the screen
        lcd_display.show_number(counter)    # displaying number
        time.sleep(.5)                      # sleeping for 500 ms
        counter += 1                        # increasing counter value

        if counter == 100:                  # exiting when 3 digits numbers are encountered
            break


if __name__ == '__main__':
    main()
