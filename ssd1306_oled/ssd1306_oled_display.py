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

Micropython extension script of SSD1306.py to interfact with OLED display both over I2C and SPI.
This script exposes additional functionalities like clearing of screen or a line.


Author: Lakhya Jyoti Nath
Date: September 2022

"""

import ssd1306
from machine import Pin, SoftI2C, SoftSPI


class OledDisplay:
    """
    OledDisplay for interacting with the 128x64 OLED display
    """

    def __init__(self, background_color=False, header_lines_to_retain: int = 0) -> None:
        """
        :param background_color: Boolean value representing is background should have color
        :param header_lines_to_retain: Integer value representing number of header lines that will be retained during scrolling
        """
        self.__oled_display = None
        self.__oled_width = None
        self.__oled_height = None

        self.__cursor_y = 0
        self.__text_height = 10                                 # text height is 10 pixel

        self.__text_color = 0 if background_color else 1        # if background_color is true, then there should not be any text color
        self.__fill_color = 1 if self.__text_color == 0 else 0  # fill color to clear screen is same as background color

        self.__header_lines = []
        self.__header_count = header_lines_to_retain

    def init_display(self, display, display_width, display_height):
        """
        Method to initalize the display where the variables are updated from the child classes
        """
        self.__oled_display = display
        self.__oled_height = display_height
        self.__oled_width = display_width

    def clear(self) -> None:
        """
        Method to clear the OLED display
        """
        # filling the display to simulate clearing of screen
        self.__oled_display.fill_rect(0, 0, self.__oled_width, self.__oled_height, self.__fill_color)
        self.__cursor_y = 0

    def clear_line(self, x: int, y: int) -> None:
        """
        Method to clear a horizontal line of text specified by postion x and y
        :param x: Int X-positon of the beginning of the line which needs to be cleared
        :param y: Int Y-positon of the beginning of the line which needs to be cleared
        """
        # filling the display from given position by a width on text-height as we need to clear a line
        self.__oled_display.fill_rect(x, y, self.__oled_width, self.__text_height, self.__fill_color)

    def show_text(self, text: str, x: int = 0, y: int = None, scroll: bool = True, ) -> None:
        """
        Method to display text on OLED display. Assuming all text will start from a new line, default value of X is set to 0
        :param text: String text to display
        :param x : Integer cursor X-position where the text should be displayed
        :param y : Integer cursor Y-position where the text should be displayed
        :param scroll: Boolean value indicating if the screen should scroll while displaying the new text
        """
        if self.__header_count > 0 and len(self.__header_lines) != self.__header_count:
            self.__header_lines.append(text)

        # using existing cursor position, if no position is passed
        if not y:
            y = self.__cursor_y

        if y >= self.__oled_height - self.__text_height:
            if scroll:
                # scroll text on Y-axis by text height
                self.__oled_display.scroll(0, self.__text_height * -1)
                y -= self.__text_height

                header_y_position = 0
                for _line in self.__header_lines:
                    self.clear_line(0, header_y_position)
                    self.__oled_display.text(_line, 0, header_y_position, self.__text_color)
                    header_y_position += self.__text_height

                # as the screen has been scrolled, there a few pixels of the last line, clearing the last line
                self.clear_line(0, y)
            else:
                # clearing screen when scoll is not set
                self.clear()
                y = 0

        # displaying input text
        self.__oled_display.text(text, x, y, self.__text_color)
        self.__oled_display.show()

        # updating y position of the cursor for the next line
        self.__cursor_y = y + self.__text_height


class OledDisplayI2C(OledDisplay):
    """
    OledDisplay for interacting with the 128x64 OLED display via I2C aka IIC
    """

    def __init__(self,  background_color=False, header_lines_to_retain: int = 0) -> None:
        """
        :param background_color: Boolean value representing is background should have color
        :param header_lines_to_retain: Integer value representing number of header lines that will be retained during scrolling
        """
        super().__init__(background_color, header_lines_to_retain)

    def init_display(self, scl: int, sda: int):
        """
        Method to initialize the display via IIC
        :param scl: Integer value IIC SCL pin number
        :param sda: Integer value IIC SDA pin number
        """
        scl_pin = Pin(scl)
        sda_pin = Pin(sda)

        # ESP32 Pin assignment
        i2c = SoftI2C(scl=scl_pin, sda=sda_pin)

        oled_width = 128
        oled_height = 64
        oled_display = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

        super().init_display(oled_display, oled_width, oled_height)


class OledDisplaySPI(OledDisplay):
    """
    OledDisplay for interacting with the 128x64 OLED display via SPI
    """

    def __init__(self, background_color=False, header_lines_to_retain: int = 0) -> None:
        """
        :param background_color: Boolean value representing is background should have color
        :param header_lines_to_retain: Integer value representing number of header lines that will be retained during scrolling
        """
        super().__init__(background_color, header_lines_to_retain)

    def init_display(self, dc: int, rst: int, cs: int,  sck: int, mosi: int, miso: int = 12) -> None:
        """
        Method to initialize the display via SPI
        :param dc: Integer value SPI DC aka Data Command pin number
        :param rst: Integer value SPI RST aka RESET pin number
        :param cs: Integer value SPI CS aka Chip Select pin number
        :param sck: Integer value SPI SCK/D0 aka Clock pin number
        :param mosi: Integer value SPI MOSI/D1 aka Data pin number
        :param miso: Integer value SPI MISO pin number
        """
        baudrate_value = 500000
        polarity_value = 1
        phase_value = 0

        dc_pin = Pin(dc)
        rst_pin = Pin(rst)
        cs_pin = Pin(cs)
        sck_pin = Pin(sck)
        mosi_pin = Pin(mosi)
        miso_pin = Pin(miso)

        spi = SoftSPI(baudrate=baudrate_value,
                      polarity=polarity_value,
                      phase=phase_value,
                      sck=sck_pin,
                      mosi=mosi_pin,
                      miso=miso_pin)

        oled_width = 128
        oled_height = 64
        oled_display = ssd1306.SSD1306_SPI(oled_width, oled_height, spi, dc_pin, rst_pin, cs_pin)

        super().init_display(oled_display, oled_width, oled_height)
