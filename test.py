
import unittest
import process as p

class TestAlignment(unittest.TestCase):

    #def __init__(self):
    #    

    def test_alignment(self):
        text = list('abcdefgabcdefgh')
        s1 = list('abc')
        s2 = list('abcdefgh')
        s3 = list('abcwwwgh')
        s4 = list('defabc')
        s5 = ['a']
        s6 = text[-1]
        s7 = list('abcwwgh')
        s8 = []

        '''
        print(p.traceback(p.calc_dp(text, s1), full_alignment=True))
        print(p.traceback(p.calc_dp(text, s2), full_alignment=True))
        print(p.traceback(p.calc_dp(text, s3), full_alignment=True))
        print(p.traceback(p.calc_dp(text, s4), full_alignment=True))

        print(p.traceback(p.calc_dp(text, s1)))
        print(p.traceback(p.calc_dp(text, s2)))
        print(p.traceback(p.calc_dp(text, s3)))
        print(p.traceback(p.calc_dp(text, s4)))
        '''

        # second argument returned is score
        a1, _ = p.traceback(p.calc_dp(text, s1))
        a2, _ = p.traceback(p.calc_dp(text, s2))
        a3, _ = p.traceback(p.calc_dp(text, s3))
        a4, _ = p.traceback(p.calc_dp(text, s4))
        a5, _ = p.traceback(p.calc_dp(text, s5))
        a6, _ = p.traceback(p.calc_dp(text, s6))
        a7, _ = p.traceback(p.calc_dp(text, s7))
        a8, _ = p.traceback(p.calc_dp(text, s8))

        self.assertTrue(2 in a1 and 9 in a1)
        # last character is included in match
        # TODO if this isn't consistent, try affine gap penalty
        # i think whatever incidental tie-breaking i have now makes this work though
        self.assertTrue(len(text) - 1 in a2, str(len(text) - 1) + ' ' + str(a2))
        self.assertTrue(len(text) - 1 in a3)
        self.assertTrue(9 in a4)

        # works for single characters regardless of position
        self.assertTrue(0 in a5 and 7 in a5)
        self.assertTrue(len(text) - 1 in a6)

        # still establishes correct end with intermittent lengths mismatches
        self.assertTrue(len(text) - 1 in a7)

        # exception was propagating to top
        #self.assertRaises(AssertionError, p.calc_dp(text, text + ['a']))

        # shouldn't get any indices by attempting to align an empty sequence
        self.assertTrue(len(a8) == 0, a8)

    def test_update(self):
        assert False

if __name__ == '__main__':
    ta = TestAlignment()
    ta.test_alignment()
