'''
TimeZone tests
'''

import unittest

from pycontrib.misc.timezone import TimezoneConverter


class TestTimezoneConverter(unittest.TestCase):

    def testTimezoneConverter(self):

        tz_conv = TimezoneConverter()

        self.assertEqual(tz_conv.iana_posix('America/Unknown'), None)

        self.assertEqual(tz_conv.iana_posix('Pacific/Niue'), 'NUT+11')
        self.assertEqual(tz_conv.iana_posix('America/Anchorage'), 'AKST+9AKDT+1,M3.2.0/02:00,M11.1.0/02:00')
        self.assertEqual(tz_conv.iana_posix('Australia/Perth'), 'WST-8')
        self.assertEqual(tz_conv.iana_posix('America/New_York'), 'EST+5EDT+1,M3.2.0/02:00,M11.1.0/02:00')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
