# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Basic word2vec example."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os
import shutil
import argparse

import tensorflow as tf

from bs4 import BeautifulSoup



this_file_path = os.path.dirname(__file__)
Diorisis_folder = os.path.join(this_file_path, "../Diorisis/")

stopwords_filename_with_prep = 'CLTK_stopwords_manual_additions.txt'
stopwords_filename_without_prep = 'CLTK_stopwords_manual_additions_no_prepositions.txt'

#########################
# Pre-processing
#########################


def get_full_sentence_lemmas(sentence, with_punct):
    l = []
    if with_punct:
        lemma_or_puncts = sentence.find_all(['lemma','punct'])
        for lemma_or_punct in lemma_or_puncts:
            if(lemma_or_punct.has_attr('entry')):
                l.append(' ' + lemma_or_punct['entry'])
            if(lemma_or_punct.has_attr('mark')):
                l.append(lemma_or_punct['mark'])
    else:
        lemmas = sentence.find_all('lemma')
        for lemma in lemmas:
            if(lemma.has_attr('entry')):
                l.append(' ' + lemma['entry'])

    return ''.join(l)

def read_xml_file(filename):
    f1 = open(filename,'r',encoding='utf8')
    f1s = f1.read()
    soup = BeautifulSoup(f1s,'lxml')
    f1.close()
    sentences = soup.find_all('sentence')
    age = soup.find('creation').find('date').get_text()
    return [sentences, age]

def write_lemmatised_file(sentences, filename, with_punct):

    f = open(filename, 'w', encoding='utf8')

    for sentence in sentences:
        lemmatised = get_full_sentence_lemmas(sentence, with_punct)
        print(lemmatised, file = f)

    f.close()

def read_and_write_all_lemmatised_files_no_punct():
    os.chdir(Diorisis_folder)
    Diorisis_files = os.listdir()

    ages_names = list()

    f_ages = open(os.path.join(Diorisis_folder, 'ages_and_names.txt'), 'w', encoding='utf8')
    for Diorisis_file in Diorisis_files:
        if(Diorisis_file.endswith('.xml')):
            print('Loading ' + Diorisis_file)
            [sentences, age] = read_xml_file(Diorisis_file)
            filename_base = Diorisis_file[:-4]
            ages_names.append([int(age), filename_base])
            print('Age is {0}'.format(age))

            filename = Diorisis_folder + filename_base + ' lemmas nopunct.txt'
            write_lemmatised_file(sentences, filename, 0)

    ages_names.sort(key = lambda x: x[0])
    for rec in ages_names:
        f_ages.write(str(rec[0]) + ', filename: ' + rec[1] + '\n')

    f_ages.close()


def get_ages_and_filenames(content):
    ages = list()
    filenames = list()
    for line in content:
        parts = line.split(', filename: ')
        ages.append(parts[0])
        filenames.append(parts[1])

    return ages, filenames

def make_BC_AD(age):
    if(age < 0):
        suffix='BC'
    else:
        suffix='AD'

    return str(abs(age)) + suffix

def make_filename_from_ages(min_age, max_age):
    return make_BC_AD(min_age) + 'to' + make_BC_AD(max_age) + '.txt'

def make_file_with_ages(out_filename, min_age, max_age):
    with open(Diorisis_folder + 'ages_and_names.txt', 'r', encoding='utf8') as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    ages, filename_bases = get_ages_and_filenames(content)

    files_read = list()

    for(f,age) in zip(filename_bases, ages):
        if(min_age <= int(age) <= max_age):
            files_read.append(Diorisis_folder + f + ' lemmas nopunct.txt')

    with open(out_filename,'wb') as wfd:
        for f in files_read:
            print('Copying in {0}'.format(f))
            with open(f,'rb') as fd:
                shutil.copyfileobj(fd, wfd, 1024*1024*30)
                #30MB per writing chunk to avoid reading big file into memory.


#########################
# Co-occurence section
#########################


# Read the data into a list of strings.
def read_data(filename):
    with open(filename, 'r', encoding='utf8') as f:
        data = tf.compat.as_str(f.read()).split()
    return data

def build_dataset(words, n_words, stopwords):
    """Process raw inputs into a dataset."""
    count = [['UNK', -1]]
    count.extend(collections.Counter(words).most_common(n_words + len(stopwords) - 1))
    dictionary = dict()
    for word, _ in count:
        if word not in stopwords:
            dictionary[word] = len(dictionary)
    data_with_stops = list()
    data = list()
    unk_count = 0
    for word in words:
        index = dictionary.get(word, 0)
        if index == 0:  # dictionary['UNK']
            unk_count += 1
        else:
            data.append(index)
        data_with_stops.append(index)

    count[0][1] = unk_count
    reversed_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
    return data_with_stops, data, count, dictionary, reversed_dictionary

def create_sparse_matrix(in_filename, vocabulary_size, skip_window, with_prep):

    #filebase = 'Homer (0012) - Iliad (001)'
    #vocabulary_size = 10000
    #skip_window = 5  # How many words to consider left and right.

    output_dir = 'output_' + in_filename[:-4].replace(' ', '_') \
        + '_vocab' + str(vocabulary_size) + '_window' + str(skip_window)

    if with_prep:
        output_dir += '_withprep'
    else:
        output_dir += '_withoutprep'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    vocabulary = read_data(in_filename)
    print('Data size', len(vocabulary))

    if with_prep:
        stopwords_filename = stopwords_filename_with_prep
    else:
        stopwords_filename = stopwords_filename_without_prep

    stopwords = read_data(stopwords_filename)
    print('Loaded {0} stop words'.format(len(stopwords)))

    # Step 2: Build the dictionary and replace rare words with UNK token.
    # Filling 4 global variables:
    # data - list of codes (integers from 0 to vocabulary_size-1).
    #   This is the original text but words are replaced by their codes
    # count - map of words(strings) to count of occurrences
    # dictionary - map of words(strings) to their codes(integers)
    # reverse_dictionary - maps codes(integers) to words(strings)
    data_with_stops, data, count, dictionary, reverse_dictionary = build_dataset(
            vocabulary, vocabulary_size, stopwords)

    counts_no_stops = list()
    for c in count:
        if c[0] not in stopwords:
            counts_no_stops.append(c)

    print('\nMost common words (excluding stopwords) (+UNK)', counts_no_stops[:40])
    print('\nOriginal text: ', ' '.join(vocabulary[:40]))
    print('\nData with UNK: ', ' '.join([reverse_dictionary[i] for i in data_with_stops[:40]]))
    print('\nData no stops: ', ' '.join([reverse_dictionary[i] for i in data[:40]]))
    print('\nLeast common words:', counts_no_stops[-4:])

    #del vocabulary  # Hint to reduce memory.

    cooc_sparse = dict()
    for i in range(0, len(data)):
        word1 = data[i]
        for j in range(-skip_window, skip_window+1):
            if j != 0 and 0 <= i + j < len(data):
                word2 = data[i+j]
                #Use pair of words ordered by number (ie how common they are) as key
                #This means that we double-count, eg in the sentence above we would count (by, number) and (number, by)
                #so only add a half.
                #
                #When we print everything to the sparse matrix file, we add each count both ways round.
                t = min(word1, word2) , max(word1, word2)
                if t in cooc_sparse:
                    cooc_sparse[t] += 0.5
                else:
                    cooc_sparse[t] = 0.5
    sorted_tuples = sorted(cooc_sparse, key = lambda x: cooc_sparse[x], reverse=True)
    print('\nMost common word pairs:')
    for i in range(10):
        t = sorted_tuples[i]
        print('{0}: {1}, {2}'.format(cooc_sparse[t], reverse_dictionary[t[0]], reverse_dictionary[t[1]]))

    f_rows = open(output_dir + '/sparsematrix.rows', 'w', encoding='utf8')
    f_cols = open(output_dir + '/sparsematrix.cols', 'w', encoding='utf8')
    f_sm   = open(output_dir + '/sparsematrix.sm', 'w', encoding='utf8')

    keys_sorted = sorted(dictionary, key = lambda x: dictionary[x])

    for k in keys_sorted[1:]:
        print(k, file = f_rows)
        print(k, file = f_cols)

    f_rows.close()
    f_cols.close()

    for t in sorted_tuples:
        print('{0} {1} {2}'.format(reverse_dictionary[t[0]], reverse_dictionary[t[1]], int(cooc_sparse[t])), file = f_sm)
        if(t[0] != t[1]):
            print('{0} {1} {2}'.format(reverse_dictionary[t[1]], reverse_dictionary[t[0]], int(cooc_sparse[t])), file = f_sm)

    f_sm.close()

    return [cooc_sparse, sorted_tuples, data, vocabulary, count, dictionary, reverse_dictionary]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
            'min_age',
            type=int,
            help='Earliest year to include')
    parser.add_argument(
            'max_age',
            type=int,
            help='Latest year to include')
    parser.add_argument(
            '-ww',
            '--window_width',
            metavar='',
            type=int,
            default=5,
            help='Number of words either side of first word to include')
    parser.add_argument(
            '-vs',
            '--vocab_size',
            metavar='',
            type=int,
            default=3000,
            help='Number of words used to create the dictionary')
    parser.add_argument(
            '-wp',
            '--with_prep',
            metavar='',
            type = int,
            default = 0,
            help = '1 to use prepositions')

    FLAGS, unparsed = parser.parse_known_args()

    texts_filename = make_filename_from_ages(FLAGS.min_age, FLAGS.max_age)
    if not os.path.exists(texts_filename):
        make_file_with_ages(texts_filename, FLAGS.min_age, FLAGS.max_age)

    with_prep = 0
    if FLAGS.with_prep:
        with_prep = 1

    [cs, st, d, v, c, d, rd] = create_sparse_matrix(texts_filename, FLAGS.vocab_size, FLAGS.window_width, with_prep)
