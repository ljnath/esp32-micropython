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

Micropython code to display current on 4 7-segment LED display without any additional IC.
This is achieved by using 2 common cathode for hours and 2 common anode for minutes.
Due to the alternate LED type, the same GPIO pins are used for displaying numbers but the LED selection is achieved by controlling the common anode/cathode pins
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


class Constants:
    """
    Constants class used in lieu of Enum as micropython doesn't support Enum yet!
    """
    @property
    def ONES(self) -> str:
        """ 
        Property for ONES digit position
        """
        return 'ONES'

    @property
    def TENS(self) -> str:
        """
        Property for TENS digit position
        """
        return 'TENS'

    @property
    def COMMON_CATHODE(self) -> str:
        """
        Property for COMMON-CATHODE position
        """
        return 'COMMON_CATHODE'

    @property
    def COMMON_ANODE(self) -> str:
        """
        Property for COMMON-ANODE position
        """
        return 'COMMON_ANODE'

    @property
    def DIGITS(self) -> dict:
        """
        all possible digits
        """
        return {
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


class LcdDisplay:
    """
    LedDisplay class to handling all the interaction with the 7-segment LED display
    """

    def __init__(self) -> None:
        gpio_pin_for_anode = 0       # anode pin for common-anode LED display
        gpio_pin_for_cathode = 4     # cathode pin for common-cathode LED display

        self.__anode_control_pin = machine.Pin(gpio_pin_for_anode, machine.Pin.OUT)
        self.__cathode_control_pin = machine.Pin(gpio_pin_for_cathode, machine.Pin.OUT)

        # all avilable segments in a 7-segment LCD display
        self.__all_segment = ('A', 'B', 'C', 'D', 'E', 'F', 'G')

        # GPIO pins for displaying the TENS digit
        self.__tens_pins = (25, 26, 16, 17, 18, 32, 33)

        # GPIO pins for displaying the ONES digit
        self.__ones_pins = (27, 14, 23, 22, 1, 12, 13)

        self.__constants = Constants()

    def __get_all_segments(self) -> tuple:
        """
        Method to get all the segment in both the ones and the tens display
        :return all_segments : a tuple of all the segments
        """
        all_segments = []
        for i in range(7):
            all_segments.append(machine.Pin(self.__ones_pins[i], machine.Pin.OUT))
            all_segments.append(machine.Pin(self.__tens_pins[i], machine.Pin.OUT))

        return tuple(all_segments)

    def __get_segments(self, position: Constants, digit: int = 8) -> tuple:
        """
        Method to get the segment responsible to display a digit.
        :param position : String value (ones or tens) which determine for which position the digit is for.
                          Based on this the pins will vary
        :param digit : Integer value, this is the digit for which the segement needs to be determined.
                       The default digit is considered as 8, where all the segment will be either ON (to display 8) or OFF (to clear display)
        :return all_segments : a tuple of all the segments either for the ones for the tens position
        """
        # determining the pins-set based on the digit position, as we are using 2 LCD display,
        # the set of pins are different
        current_set_of_pins = ()
        if position == self.__constants.ONES:
            current_set_of_pins = self.__ones_pins
        elif position == self.__constants.TENS:
            current_set_of_pins = self.__tens_pins

        # creating a dict of segments with key as A,B,C,D,E,F and G and value as instance of machine.Pin to interact with the Pin output value
        all_segments = {}
        for i in range(7):
            all_segments[self.__all_segment[i]] = machine.Pin(current_set_of_pins[i], machine.Pin.OUT)

        # casting and returning the segments applicable for given `digit`
        return tuple([value for key, value in all_segments.items() if key in self.__constants.DIGITS.get(digit)])

    def show_number(self, number, led_type: Constants):
        """
        Method to show a 2 digit number on the LCD display. 
        Based on the led_type, the anode and cathode pins are manipulated to show the number either on the common-anode or comon-cathode LED display
        :param number : Integer number to show
        :prarm led_type : Constants to determine whether the number should be displayed in the common-anode or comon-cathode LED display
        """
        ones_digit = number % 10

        if led_type == self.__constants.COMMON_ANODE:
            # turning off the common-cathode display as well as turning off all the segments in both the LED display
            self.__anode_control_pin.on()
            self.__cathode_control_pin.on()
            _ = [segment.on() for segment in self.__get_all_segments()]

            # displaying ones in common anode
            segments_to_off = self.__get_segments(self.__constants.ONES, ones_digit)
            _ = [segment.off() for segment in segments_to_off]

            # calculating and displaying tens in common anode
            if number > 9:
                tens_digit = number // 10
                segments_to_off = self.__get_segments(self.__constants.TENS,  tens_digit)
                _ = [segment.off() for segment in segments_to_off]

        elif led_type == self.__constants.COMMON_CATHODE:
            # turning off the common-anode display as well as turning off all the segments in both the LED display
            self.__cathode_control_pin.off()
            self.__anode_control_pin.off()
            _ = [segment.off() for segment in self.__get_all_segments()]

            # displaying ones in common cathode
            segments_to_lit = self.__get_segments(self.__constants.ONES, ones_digit)
            _ = [segment.on() for segment in segments_to_lit]

            # calculating and displaying tens in common cathode
            if number > 9:
                tens_digit = number // 10
                segments_to_lit = self.__get_segments(self.__constants.TENS,  tens_digit)
                _ = [segment.on() for segment in segments_to_lit]


def main():
    """
    Driver function
    """
    # intermediate sleep value, impacts the switching of display
    sleep_value = 200

    lcd_display = LcdDisplay()
    constants = Constants()

    while True:
        current_time = time.localtime()

        time.sleep_ms(sleep_value)
        lcd_display.show_number(current_time[3], constants.COMMON_CATHODE)

        time.sleep_ms(sleep_value)
        lcd_display.show_number(current_time[4], constants.COMMON_ANODE)

        time.sleep(.3)


if __name__ == '__main__':
    main()
