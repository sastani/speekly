
import unittest
import process as p

class TestAlignment(unittest.TestCase):

    def __init__(self):
        self.samp_text = list('abcdefgabcdefgh')
        self.s1 = list('abc')
        self.s2 = list('abcdefgh')
        self.s3 = list('abcwwwgh')
        self.s4 = list('abcwwgh')

    def test_alignment(self):
        text = self.samp_text

        print(p.traceback(p.calc_dp(text, self.s1, verbose=True), full_alignment=True))
        '''
        print(p.traceback(p.calc_dp(text, self.s2), full_alignment=True))
        print(p.traceback(p.calc_dp(text, self.s3), full_alignment=True))
        print(p.traceback(p.calc_dp(text, self.s4), full_alignment=True))
        '''

