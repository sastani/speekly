
import numpy as np
from nltk.tokenize import word_tokenize
import time


def score(word_a, word_b):
    if word_a == word_b:
        return 1
    else:
        return 0


# TODO numba this and traceback
def calc_dp(text, snippet, indel=0, verbose=False):
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
    # TODO TODO is indel correctly applied? see test snip2
    # affine gap?

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


def traceback(dp_info):
    """
    Returns set of indices of last position in text scored as best in the dynamic programming.

    Args:
        dp_info (4-tuple of the following): 
            D (2d ndarray) the dynamic programming table
            T (2d ndarray) the traceback information
            text (list-like of "nice" strings) the text to be read
            snippet (like-like of strings) what was fed back from API
    """

    D, T, text, snippet = dp_info
    #print(text)
    #print(snippet)

    i, j = T.shape
    i -= 1
    j -= 1

    # need to start from all maxima on bottom and right of dp table
    max_score = max([np.max(D[:,-1]), np.max(D[-1,:])])
    #print('max_score', max_score)

    maxima = []
    for i in range(D.shape[0]):
        if D[i,D.shape[1]-1] == max_score:
            maxima.append((i,D.shape[1]-1))

    for j in range(D.shape[1]):
        if D[D.shape[0]-1,j] == max_score:
            maxima.append((D.shape[0]-1,j))

    #print('indices w/ max score on edge of dp table', maxima)

    alignments = []
    end_indices = set()

    #print(D)
    #print(T)

    for m in maxima:
        i, j = m
        i -= 1
        j -= 1

        alignment = []

        while i >= 0 and j >= 0:
            #print(i, j)
            if T[i,j] == b'm':
                alignment += snippet[j]

                # if we only want last index of any character called as a match
                # we can return early
                # (use this after debugging whether whole alignment seems reasonable)

                # should be the index in the text (therefore i)
                end_indices.add(i)

                i -= 1
                j -= 1

            elif T[i,j] == b'r':
                # does matter here. may be source of bugs.
                alignment += '_' #text[i]
                i -= 1

            elif T[i,j] == b'l':
                # does matter here. may be source of bugs.
                alignment += snippet[i] #'*'
                j -= 1

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

        # TODO make set of indices as well
        alignments.append(alignment[::-1])

    # TODO update tests to expect this output format
    return alignment, end_indices, max_score


class TextProgress(object):

    def __init__(self, text, dynamic=False):
        # TODO tokenize
        self.text = text
        self.token_seq = word_tokenize(text)

        self.marker = 0
        # list of words attempted to either floats or right / wrong
        # TODO default dict (not read)
        self.progress = dict()

        self.correct = np.empty(len(text)) * np.nan
        self.last_update = -1
        self.last_marker = -1
        self.estimate_rate = 0
        self.min_score = 0
        self.dynamic = dynamic

        # Taylor entered this random filter value
        self.align_weight = 0.8

        # controls length of subsequence we try to align to text
        # could be a function of text length as well
        #self.memory = 10


    def align(self, snippet):
        """
        Returns a list of end indices of alignments and the best score.
        """
        return traceback(calc_dp(self.token_seq, snippet))

    
    def progress_dict():
        d = dict()
        d['marker'] = self.marker
        d['progress'] = 


    def update(self, interpretations):
        """
        Aligns new_text to token_seq, weighted by our estimate before receiving any data.
        Can explicitly account for time passed, etc.

        Args:
            interprations: list of tuples ((snippet, confidence), ...)
                snippets should be strings of standardized text
                confidences should be floats
        """

        # TODO could use same dp on lists created from each word to calculate a similarity
        # score for the word, which we could then threshold

        if self.dynamic:
            if self.last_update == -1:
                elapsed = 0
            else:
                elapsed = time.time() - self.last_update

            self.last_marker = self.marker

        # if this really simple solution actually works best, maybe just use that
        # or weight as alignment is
        #self.marker += len(new_text)

        # TODO run alignments with each of few most confident responses
        # penalize reader more for the string matching text best coming from a lower confidence

        max_score = 0   # 0 is min possible score if no scores < 0
        best_indices = set()

        # TODO may not work if score can go below zero. set to min possible otherwise.
        for index_set, score in map(lambda x: x[2], map(self.align, interpretations)):
            # not dealing with ties for now
            if score > max_score:
                max_score = score
                best_indices = index_set

        # if there are multiple tied alignments, take the one closest to the current marker
        # TODO would be better to use prediction rather than raw marker
        if len(best_indices) > 1:
            indices_copy = set(best_indices)

            closest = indices_copy.pop()
            min_dist = abs(closest - marker)

            while len(indices_copy) > 0:
                curr = indices_copy.pop()
                distance = abs(curr - marker)
                if distance < min_dist:
                    min_dist = distance
                    closest = curr

        elif len(best_indices) == 1:
            align_end_index = best_indices.pop()

        # len(indices) == 0
        else:
            # TODO
            print('no alignment found.')

        update_scores(alignment, align_end_index)

        # update our estimate of where the reader is in the text
        if self.dynamic:
            self.marker = round(self.align_weight * align_end_index + \
                    (1 - self.align_weight) * self.marker + self.estimated_rate * elapsed)

        # TODO will probably want align_weight cloes to 1 for this case
        else:
            self.marker = round(self.align_weight * align_end_index + \
                    (1 - self.align_weight) * self.marker)

        if self.dynamic:
            # update estimated reading rate
            # words per second (change in marker / sampling interval)
            # not allowing the estimate to include them reading backwards
            if elapsed != 0:
                self.estimated_rate = max(0, self.last_marker - self.marker)

            self.last_update = time.time()

        # TODO signal new words correct or incorrect

        self.send_to_client(self.progress_dict())
        
