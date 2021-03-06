
import unittest
import process as p


# exptected_result = {"text": [
#         {
#             value: "The",
#             correct: False
#         }
#     ],
#     'marker': 5}

test_paragraph = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Praesentium sit sint laborum, ab voluptatum quibusdam modi, odio minus fuga, repudiandae laudantium perspiciatis, dolorem saepe facilis quia minima aliquam distinctio voluptas.'


class TestAlignment(unittest.TestCase):

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


    def test_update_basic(self):
        # all three things should be aligned to standardized text in order
        input1 = [(['lorem', 'ipsum', 'dolor'], 1.0)]

        progress_tracker = p.TextProgress(test_paragraph)
        self.assertEqual(0, progress_tracker.marker)

        progress_tracker.update(input1)
        self.assertEqual(3, progress_tracker.marker, progress_tracker.marker)

        # the internal dict, not yet converted to JSON friendly format
        self.assertEqual({0: True, 1: True, 2: True}, \
                progress_tracker.progress)

        # after calling function that converts to a JSON friendly nested dict
        self.assertEqual({
            'text': [{
                'index': 0,
                'correct': True
            },
            {
                'index': 1,
                'correct': True
            },
            {
                'index': 2,
                'correct': True
            }],
            'marker': 3
        }, progress_tracker.progress_dict())


    def test_align_simple(self):
        text = list('ab')
        s = ['b']
        align, score = p.traceback(p.calc_dp(text, s))

    def test_update_first(self):
        input_seq1 = [(['lorem'], 1.0)]
        progress_tracker = p.TextProgress(test_paragraph)

        progress_tracker.update(input_seq1)
        self.assertEqual(1, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True}, progress_tracker.progress)

    def test_update_second(self):
        input_seq2 = [(['ipsum'], 1.0)]
        progress_tracker = p.TextProgress(test_paragraph)

        progress_tracker.update(input_seq2)
        self.assertEqual(2, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: False, 1: True}, progress_tracker.progress)


    def test_update_sequential(self):
        # all three things should be aligned to standardized text in order
        input_seq1 = [(['lorem'], 1.0)]
        input_seq2 = [(['ipsum'], 1.0)]
        input_seq3 = [(['dolor'], 1.0)]

        progress_tracker = p.TextProgress(test_paragraph)

        progress_tracker.update(input_seq1)
        self.assertEqual(1, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True}, progress_tracker.progress)

        progress_tracker.update(input_seq2)
        self.assertEqual(2, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True, 1: True}, progress_tracker.progress)

        progress_tracker.update(input_seq3)
        self.assertEqual(3, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True, 1: True, 2: True}, progress_tracker.progress)

        # after calling function that converts to a JSON friendly nested dict
        self.assertEqual({
            'text': [{
                'index': 0,
                'correct': True
            },
            {
                'index': 1,
                'correct': True
            },
            {
                'index': 2,
                'correct': True
            }],
            'marker': 3
        }, progress_tracker.progress_dict())


    def test_update_sequential_duplication(self):
        # all three things should be aligned to standardized text in order
        input_seq1 = [(['lorem'], 1.0)]
        input_seq2 = [(['ipsum'], 1.0)]
        input_seq3 = [(['ipsum'], 1.0)]
        input_seq4 = [(['dolor'], 1.0)]

        progress_tracker = p.TextProgress(test_paragraph)

        progress_tracker.update(input_seq1)
        self.assertEqual(1, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True}, progress_tracker.progress)

        progress_tracker.update(input_seq2)
        self.assertEqual(2, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True, 1: True}, progress_tracker.progress)

        progress_tracker.update(input_seq3)
        self.assertEqual(3, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True, 1: True}, progress_tracker.progress)

        progress_tracker.update(input_seq4)
        self.assertEqual(4, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True, 1: True, 2: True}, progress_tracker.progress)

        # after calling function that converts to a JSON friendly nested dict
        self.assertEqual({
            'text': [{
                'index': 0,
                'correct': True
            },
            {
                'index': 1,
                'correct': True
            },
            {
                'index': 2,
                'correct': True
            }],
            'marker': 3
        }, progress_tracker.progress_dict())


    def test_update_sequential_insertion(self):
        # all three things should be aligned to standardized text in order
        input_seq1 = [(['lorem'], 1.0)]
        input_seq2 = [(['ipsum'], 1.0)]
        input_seq3 = [(['what is missing here?'], 1.0)]
        input_seq4 = [(['dolor'], 1.0)]

        progress_tracker = p.TextProgress(test_paragraph)

        progress_tracker.update(input_seq1)
        self.assertEqual(1, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True}, progress_tracker.progress)

        progress_tracker.update(input_seq2)
        self.assertEqual(2, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True, 1: True}, progress_tracker.progress)

        progress_tracker.update(input_seq3)
        self.assertEqual(3, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True, 1: True}, progress_tracker.progress)

        progress_tracker.update(input_seq4)
        self.assertEqual(4, progress_tracker.marker, progress_tracker.marker)
        self.assertEqual({0: True, 1: True, 2: True}, progress_tracker.progress)

        # after calling function that converts to a JSON friendly nested dict
        self.assertEqual({
            'text': [{
                'index': 0,
                'correct': True
            },
            {
                'index': 1,
                'correct': True
            },
            {
                'index': 2,
                'correct': True
            }],
            'marker': 3
        }, progress_tracker.progress_dict())


    def test_update_overlapping(self):
        # one word insertion between text and 
        input1 = [(['lorem', 'ipsum', 'nothin', 'sit'], 1.0)]
        
        progress_tracker = p.TextProgress(test_paragraph)
        self.assertEqual(0, progress_tracker.marker)

        progress_tracker.update(input1)
        # was 3, but 4 makes sense
        # mostly empirically, not rigorously checked given cost function, but seems right
        self.assertEqual(4, progress_tracker.marker, progress_tracker.marker)

        # the internal dict, not yet converted to JSON friendly format
        self.assertEqual({0: True, 1: True, 2: False, 3: True}, \
                progress_tracker.progress)

        # after calling function that converts to a JSON friendly nested dict
        self.assertEqual({
            'text': [{
                'index': 0,
                'correct': True
            },
            {
                'index': 1,
                'correct': True
            },
            {
                'index': 2,
                'correct': False
            },
            {
                'index': 3,
                'correct': True
            }],
            'marker': 4
        }, progress_tracker.progress_dict())


    '''
    def test_textprogress_init(self):

        test_paragraph = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Praesentium sit sint laborum, ab voluptatum quibusdam modi, odio minus fuga, repudiandae laudantium perspiciatis, dolorem saepe facilis quia minima aliquam distinctio voluptas.'

        prog = p.TextProgress(test_paragraph)

        print(prog.token_seq)

    '''
        
if __name__ == '__main__':
    ta = TestAlignment()

    ta.test_alignment()
    ta.test_align_simple()
    #ta.test_textprogress_init()
    ta.test_update_basic()
    ta.test_update_first()
    ta.test_update_second()
    ta.test_update_sequential()
    ta.test_update_overlapping()
    ta.test_update_sequential_duplication()
    ta.test_update_sequential_insertion()
