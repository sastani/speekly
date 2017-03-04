
import numpy as np
from nltk.tokenize import word_tokenize


def score(word_a, word_b):
    if word_a == word_b:
        return 1
    else:
        return 0


# TODO numba this and traceback
def calc_dp(text, snippet, indel=-12, verbose=False):
    """
    Calculates dynamic programming table and traceback information for snippet and text.

    Args:
        text (list-like): list of "nice" strings comprising text to be read
        snippet (list-like): list of strings returned from API
    """
    # TODO i want indel to not be applied at beginning of alignment, but at end
    # not sure if this accomplishes that... the problems dp solves are usually symmetric

    if verbose:
        print(text, snippet)

    assert len(text) >= len(snippet), 'length of text should be longer than chunks ' + \
            'returned from API'

    D = np.zeros((len(text) + 1, len(snippet) + 1))
    T = np.chararray((len(text), len(snippet)))

    # just commenting this portion should convert the algorithm to 
    # a solution to the longest common subSTRING problem
    '''
    for i in range(D.shape[0]):
        D[i,0] = i * indel

    for j in range(D.shape[1]):
        D[0,j] = j * indel
    '''

    # TODO it seems top row of T is not set
    # all is set to 'r' as well
    for i in range(1, D.shape[0]):
        for j in range(1, D.shape[1]):
            match = D[i-1,j-1] + score(text[i-1], snippet[j-1])
            skip_text = D[i-1,j] + indel
            skip_snippet = D[i,j-1] + indel

            if verbose:
                print(i, j, text[i-1], snippet[j-1], match, skip_text, skip_snippet)

            best = max([match, skip_text, skip_snippet])
            D[i,j] = best

            if best == match:
                T[i-1,j-1] = 'm'
            elif best == skip_text:
                T[i-1,j-1] = 'r'
            elif best == skip_snippet:
                T[i-1,j-1] = 'l'

            if verbose:
                print(T[i-1,j-1])
                print(D)
                print(T)
               
    return D, T, text, snippet


# TODO ultimately want the last index of alignment out of this, i think
def traceback(dp_info, full_alignment=False):
    """
    Returns index of last position in text scored as a match in the dynamic programming.

    Args:
        dp_info (4-tuple of the following): 
            D (2d ndarray) the dynamic programming table
            T (2d ndarray) the traceback information
            text (list-like of "nice" strings) the text to be read
            snippet (like-like of strings) what was fed back from API
    """

    D, T, text, snippet = dp_info
    print(text)
    print(snippet)

    i, j = T.shape
    i -= 1
    j -= 1

    alignment = ''

    while i > 0 and j > 0:
        #print(i, j)
        if T[i,j] == b'm':
            i -= 1
            j -= 1
            # doesn't matter which string you draw from if they match
            alignment += text[i]

            # if we only want last index of any character called as a match
            # we can return early
            # (use this after debugging whether whole alignment seems reasonable)
            if not full_alignment:
                # should be the index in the text (therefore i)
                return i

        elif T[i,j] == b'r':
            i -= 1
            # does matter here. may be source of bugs.
            alignment += text[i]

        elif T[i,j] == b'l':
            j -= 1
            # does matter here. may be source of bugs.
            alignment += '_'

        else:
            print(T[i,j])
            print(D)
            print(T)
            assert False, 'all chars in T should be either m, r, or l'

        # this would be if we wanted the index of the first matching character, not last
        '''
        if D[i,j] == 0:
            break
        '''
    return alignment[::-1]


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

    def align(self, snippet):
        return traceback(calc_dp(self.token_seq, snippet))

    def update(self, new_text):
        """
        Aligns new_text to token_seq, weighted by our estimate before receiving any data.
        Can explicitly account for time passed, etc.
        """

        # TODO change. simple filler implementation
        self.marker += len(new_text)
        # TODO signal new words correct or incorrect

        '''
        # should get an index from update
        a = self.align(new_text)
        print(a)
        '''


