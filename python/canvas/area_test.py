#!/usr/bin/env python
# coding=utf-8
'''
unit test for class area
Magtroid @ 2019-05-09 16:11
'''

import unittest

import area

class AreaTest(unittest.TestCase):
    # all function should start with test
    def test_struct(self):
        new_area = area.Area([10, 20])
        self.assertEqual([10, 20], new_area.struct())
        
if __name__ == '__main__':
    unittest.main()
