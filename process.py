
import numpy as np
from ntlk.tokenize import word_tokenize

class TextProgress(object):

    def __init__(self, text):
        # TODO tokenize
        self.text = text
        self.token_seq = word_tokenize(text)
        self.position = 0
        self.correct = np.empty(len(text)) * np.nan

        # controls length of subsequence we try to align to text
        # could be a function of text length as well
        self.memory = 10


    def score(word_a, word_b):
        if word_a == word_b:
            return 1
        else:
            return 0


    # TODO numba this and traceback
    def align(s1, s2, indel=1):
        D = np.zeros((len(s1) + 1, len(s2) + 1))
        T = np.chararray((len(s1), len(s2))

        # just commenting this portion should convert the algorithm to 
        # a solution to the longest common subSTRING problem
        '''
        for i in range(D.shape[0]):
            D[i,0] = i * indel

        for j in range(D.shape[1]):
            D[0,j] = j * indel
        '''

        for i in range(1, D.shape[0]):
            for j in range(1, D.shape[1]):
                match = D[i-1,j-1] + score(s1[i-1], s2[j-1])
                skip_s1 = D[i-1,j] + indel
                skip_s2 = D[i,j-1] + indel

                best = max([match, skip_s1, skip_s2])
                D[i,j] = best

                if best == match:
                    T[i-1,j-1] = 'm'
                elif best == skip_s1:
                    T[i-1,j-1] = 'r'
                elif best == skip_s1:
                    T[i-1,j-1] = 'l'
                   
        return D, T, s1, s2


    def traceback(dp_info):
        D, T, s1, s2 = dp_info

        i, j = T.shape
        alignment = ''

        # TODO can stop once get to zeros
        while i > 0 and j > 0:
            if T[i,j] == 'm':
                i -= 1
                j -= 1
                # doesn't matter which string you draw from if they match
                alignment += s1[i]

            elif T[i,j] == 'r':
                i -= 1
                # does matter here. may be source of bugs.
                alignment += s1[i]

            elif T[i,j] == 'l':
                j -= 1
                # does matter here. may be source of bugs.
                alignment += '_'


            '''
            if D[i,j] == 0:
                break
            '''

        



    def update(new_text):
        """
        Aligns new_text to token_seq, weighted by our estimate before receiving any data.
        """

        a = traceback(align(new_text, self.token_seq))

        print(a)


