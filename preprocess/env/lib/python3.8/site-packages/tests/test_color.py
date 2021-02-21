import unittest
import warnings
from gmplot.color import _is_valid_hex_color, _get_hex_color

class ColorTests(unittest.TestCase):
    def setUp(self):
        self.longMessage = True

    def test_is_valid_hex_color(self):
        # Test valid hex colors:
        VALID_HEX_COLORS = [
            '#000000',
            '#FFCC00',
            '#ae44BB'
        ]

        for color in VALID_HEX_COLORS:
            self.assertEqual(_is_valid_hex_color(color), True, "'%s' should be a valid hex color" % color)

        # Test invalid hex colors:
        INVALID_HEX_COLORS = [
            '#FC0',
            '#GFCC00',
            '#0000000',
            '11ee22',
            'red',
            []
        ]

        for color in INVALID_HEX_COLORS:
            self.assertEqual(_is_valid_hex_color(color), False, "'%s' should be an invalid hex color" % color)

    def test_get_hex_color_code(self):
        # Test valid aliases of red:
        for color in ['r', 'red', '#FF0000']:
            self.assertEqual(_get_hex_color(color), '#FF0000', "'%s' should be a valid alias for 'red'" % color)

        # Test invalid colours:
        INVALID_COLORS = [
            'colorthatdoesntexist',
            '#abc'
        ]

        for color in INVALID_COLORS:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                self.assertEqual(_get_hex_color(color), '#000000', "'%s' should be an invalid color" % color)
                self.assertEqual(len(w), 1, "'%s' should raise a single warning" % color)
                self.assertTrue(issubclass(w[-1].category, UserWarning), "'%s' should raise a 'UserWarning'" % color)
