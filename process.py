
import re
import io
import numtoword
import numpy as np
from nltk.tokenize import word_tokenize
import time

verbose = False

#######################################################################################
# Sina's text processing functions

def process_text(in_file, homo_dic):
    f = open(in_file, "r")
    words = []
    line = f.readline()
    while line:
        curr_words = line.split()
        for word in curr_words:
            word = process_string(word, homo_dic)
            words.append(word)
        line = f.readline()
    return words

def process_string(word, homo_dic):
    # if word.isdigit():
    #     word = numtoword.numtoword(word)
    # else:
    #     word = re.sub(r'[^a-zA-Z]', '', word)
    #     word = word.lower()
    #     if word in homo_dic:
    #         word = homo_dic[word]

    word = re.sub(r'[^a-zA-Z]', '', word)
    word = word.lower()
    if word in homo_dic:
        word = homo_dic[word]
        
    return word

def load_homophones(in_file='./homophones-clean.txt'):
    related_words = {}
    f = open(in_file, "r")
    line = f.readline()
    key_value = line.split(",")
    related_words[key_value[0]] = key_value[1]
    return related_words

def process_block(block, homo_dict):
    sequence = []
    block = block.replace('-', ' ')
    for s in block.split():
        proc_word = process_string(s, homo_dict)
        #split in case of return of "sixty four"
        proc_words = proc_word.split()
        for w in proc_words:
            sequence.append(w)
    
    return sequence

#######################################################################################
# Alignment functions / backend state

# TODO pass Sina's function as is_equivalent, earlier in process
def score(word_a, word_b, is_equivalent=lambda a, b: a == b):
    if is_equivalent(word_a,  word_b):
        return 1
    else:
        # TODO any cases where i am assuming nonnegative cost / util
        return -1


# TODO numba this and traceback
def calc_dp(text, snippet, indel=0):
    """
    Calculates dynamic programming table and traceback information for snippet and text.

    Args:
        text (list-like): list of "nice" strings comprising text to be read
        snippet (list-like): list of strings returned from API
    """
    # TODO i want indel to not be applied at beginning of alignment, but at end
    # not sure if this accomplishes that... the problems dp solves are usually symmetric

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

            #if verbose:
            #    print(D)
            #    print(T)
               
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

    if verbose:
        print('indices w/ max score on edge of dp table', maxima)

    alignments = dict()

    for m in maxima:
        i, j = m
        i -= 1
        j -= 1

        if verbose:
            print('')
            print('new maxima')

        #print('maxima', m)

        end_index = -1
        curr_alignment = []

        # TODO need to parse these alignments into scores of words prior to marker
        while i >= 0 and j >= 0:
            if verbose:
                print('CURR_ALIGNMENT', curr_alignment)
            #print('before ifs', i, j)

            if T[i,j] == b'm':
                curr_alignment += [snippet[j]]

                if verbose:
                    print('SNIPPET J IN M', snippet[j])
                    print('text i', text[i])

                # if we only want last index of any character called as a match
                # we can return early
                # (use this after debugging whether whole alignment seems reasonable)

                # should be the index in the text (therefore i)
                if end_index == -1:
                    end_index = i

                i -= 1
                j -= 1

            # TODO revisit indexing. sanity check. switch i & j decrement?
            elif T[i,j] == b'r':
                # does matter here. may be source of bugs.
                if verbose:
                    print('CHARACTER ABSENT FROM TEXT (R)')

                curr_alignment += [None] #text[i]
                i -= 1

            elif T[i,j] == b'l':
                # does matter here. may be source of bugs.
                #print('SNIPPET TYPE IN L', type(snippet[j]))
                # TODO check still passes initial tests w/ snippet[j]
                if verbose:
                    print('SNIPPET J IN L', snippet[j])
                curr_alignment += [snippet[j]] #'*'
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

        if end_index != -1:
            alignments[end_index] = curr_alignment[::-1]

    '''
    print(T)
    print(D)
    print(alignments)
    print(max_score)
    '''

    return alignments, max_score


class TextProgress(object):

    def __init__(self, text, dynamic=False):
        #self.text = text
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
        self.align_weight = 1

        # controls length of subsequence we try to align to text
        # could be a function of text length as well
        #self.memory = 10

        self.homophone_dict = load_homophones()
        self.token_seq = self.standardize_block(text)


    def align(self, snippet):
        """
        Returns a list of end indices of alignments and the best score.
        """
        
        return traceback(calc_dp(self.token_seq, snippet))

    
    def progress_dict(self):
        d = dict()
        d['marker'] = self.marker
        d['text'] = [{'index': i, 'correct': self.progress[i]} for i, w in enumerate(self.token_seq)\
                if i in self.progress]
        return d


    def update_scores(self, alignment, length_diff):
        '''
        start_index = align_end_index - len(alignment)

        # '_' is magic character for a word that was in token_seq but not
        # in the snippet aligned to it
        correct = [not a is None for a in alignment]

        for i, c in enumerate(correct):
            self.progress[i + start_index] = c
        '''
        '''
        i = len(alignment) - 1
        while i >= 0:
            if not alignment[i] is None:
        '''

        print('self.progress', self.progress)
        print('input alignment', alignment)
        print('lendiff', length_diff)

        # words we have skipped that are not already scored should be False
        # words once marked false but now true will probably (?) be in alignment
        # anyway
        for i in range(length_diff):
            if not i in self.progress:
                self.progress[i] = False

        if verbose:
            print(alignment)
            print(len(alignment))

        non_none_indices = [i for i, e in enumerate(alignment) if not e is None]

        if verbose:
            print('NON_NONE_INDICES', non_none_indices)

        last_non_none = max(non_none_indices)
        correct = [not a is None for a in alignment[:last_non_none + 1]]

        for i, a in enumerate(correct):
            self.progress[i + length_diff] = a


    def update(self, interpretations):
        """
        Aligns interpretations to token_seq, weighted by our estimate before receiving any data.
        Can explicitly account for time passed, etc.

        Args:
            interprations: list of tuples ((snippet, confidence), ...)
                snippets should be lists of strings of standardized text
                confidences should be floats
        """

        if verbose:
            print('')
            print('')
            print('CALLING UPDATE WITH INTERPRETATIONS:', interpretations)

        # standardize everything we get 
        interpretations = [([self.standardize_string(e) for e in snippet], confidence) \
                for snippet, confidence in interpretations]

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
        best_alignment = None

        # TODO may not work if score can go below zero. set to min possible otherwise.
        for alignment, score in map(lambda x: self.align(x[0]), interpretations):

            # not dealing with ties for now
            if score >= max_score:
                max_score = score
                print(alignment)
                best_alignment = alignment

        assert not best_alignment is None, 'best_alignment was not updated'

        # if there are multiple tied alignments, take the one closest to the current marker
        # TODO would be better to use prediction rather than raw marker
        if len(best_alignment) > 1:
            closest = None
            min_dist = None

            for end_index in best_alignment.keys():
                if closest == None and min_dist == None:
                    closest = end_index
                    min_dist = abs(closest - self.marker)

                else:
                    # TODO remove these if works a few times
                    assert not closest is None
                    assert not min_dist is None

                    distance = abs(end_index - self.marker)
                    if distance <= min_dist:
                        min_dist = distance
                        closest = end_index 
            align_end_index = closest

        elif len(best_alignment) == 1:
            align_end_index = list(best_alignment.keys()).pop()

        # len(indices) == 0
        else:
            # TODO
            # fail?
            print('no alignment found.')
            return

        alignment = best_alignment[align_end_index]
        '''
        print('alignment right before update_score', alignment)
        print(len(alignment))
        '''
        len_diff = len(self.token_seq) - len(alignment)
        self.update_scores(alignment, len_diff)

        # update our estimate of where the reader is in the text
        if self.dynamic:
            self.marker = round(self.align_weight * (align_end_index + 1) + \
                    (1 - self.align_weight) * self.marker + self.estimated_rate * elapsed)

        # TODO will probably want align_weight cloes to 1 for this case
        else:
            self.marker = round(self.align_weight * (align_end_index + 1) + \
                    (1 - self.align_weight) * self.marker)

        if self.dynamic:
            # update estimated reading rate
            # words per second (change in marker / sampling interval)
            # not allowing the estimate to include them reading backwards
            if elapsed != 0:
                self.estimated_rate = max(0, self.last_marker - self.marker)

            self.last_update = time.time()

        # TODO signal new words correct or incorrect

        return self.progress_dict()

    
    def standardize_string(self, string):
        """
        """
        return process_string(string, self.homophone_dict)


    def standardize_block(self, block):
        """
        """
        return process_block(block, self.homophone_dict)
