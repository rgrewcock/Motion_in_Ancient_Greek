import argparse
import os
import io
import numpy

import csv
from itertools import izip

from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity


import matplotlib.pyplot as plt


def plot_with_labels(co_matrix, ids, labels, filename,figinches):
  assert co_matrix.shape[0] >= len(labels), 'More labels than embeddings'
  plt.figure(figsize=(figinches, figinches))  # in inches
  for i, label in zip(ids, labels):
    x = co_matrix[i, 0]
    y = co_matrix[i, 1]
    plt.scatter(x, y)
    plt.annotate(
        label,
        xy=(x, y),
        xytext=(5, 2),
        textcoords='offset points',
        ha='right',
        va='bottom')

  plt.autoscale(enable=True, axis ='both', tight=True)
  plt.savefig(filename)


def plot_space_with_verbs(this_space, verb_ids, n_plot, filename):

    if n_plot > 30:
        figinches = 50
    else:
        figinches = 50

    ids = [i for i in xrange(n_plot)]
    ids.extend(verb_ids)
    labels = [this_space.id2row[i].decode('utf-8') for i in ids]
    plot_with_labels(this_space.cooccurrence_matrix, ids, labels, filename, figinches)


#This is copied and slightly modified from inside the DISSECT code, to allow directly specifying a vector
#to get the neighbours of.
def get_neighbours_vector(space1, vector, no_neighbours, similarity,
                       space2=None):
        """
        Computes the neighbours of a word in the semantic space.

        Args:
            word: string, target word
            no_neighbours: int, the number of neighbours desired
            similarity: of type Similarity, the similarity measure to be used
            space2: Space type, Optional. If provided, the neighbours are
                retrieved from this space, rather than the current space.
                Default, neighbours are retrieved from the current space.

        Returns:
            list of (neighbour_string, similarity_value) tuples.

        Raises:
            KeyError: if the word is not found in the semantic space.

        """

        #vector = self.get_row(word)

        if space2 is None:
            id2row = space1.id2row
            sims_to_matrix = similarity.get_sims_to_matrix(vector,
                                                          space1.cooccurrence_matrix)
        else:
            mat_type = type(space2.cooccurrence_matrix)
            if not isinstance(vector, mat_type):
                vector = mat_type(vector)

            sims_to_matrix = similarity.get_sims_to_matrix(vector,
                                         space2.cooccurrence_matrix)
            id2row = space2.id2row

        sorted_perm = sims_to_matrix.sorted_permutation(sims_to_matrix.sum, 1)
        no_neighbours = min(no_neighbours, len(id2row))
        result = []

        for count in range(no_neighbours):
            i = sorted_perm[count]
            result.append((id2row[i], sims_to_matrix[i,0]))

        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filebase',
            type=str,
            help='Name of folder containing data'
            )
    parser.add_argument('verbs_filename',
            type=str,
            help='Name of file containing list of verbs to use'
            )
    parser.add_argument('verbs_for_mean_filename',
            type=str,
            help = 'Name of file with restricted set of verbs'
            )
    parser.add_argument('-nn','--number_neighbours',
            type=int,
            default=200,
            help='Number of neighbours to output in neighbours_list.csv'
            )

    parser.add_argument('-nmn','--number_mean_neighbours',
            type=int,
            default=1500,
            help='Number of neighbours to output in distance_to_mean.csv'
            )


    FLAGS, unparsed = parser.parse_known_args()

#Example inputs, for testing:
#
#    FLAGS.filebase = 'output_2000BCto2000AD_vocab20000_window5'
#    FLAGS.verbs_filename = 'verbs1.txt'
#    FLAGS.min_similarity = 0.7
#    FLAGS.number_neighbours = 30
#    FLAGS.number_mean_neighbours = 500

    pickles = [f for f in os.listdir(FLAGS.filebase) if f.endswith('.pkl')]

    if(len(pickles) == 0):
        print 'No pickles found in directory ' + FLAGS.filebase + '!'
        exit()

    pickle = pickles[0]
    fname = FLAGS.filebase + '/' + pickle
    this_space = io_utils.load(fname)

    f_verbs = io.open(FLAGS.verbs_filename, 'r', encoding='utf8')
    verbs = list(f_verbs)
    f_verbs.close()

    f_verbs_for_mean = io.open(FLAGS.verbs_for_mean_filename, 'r', encoding='utf8')
    verbs_for_mean = list(f_verbs_for_mean)
    f_verbs_for_mean.close()

    verbs_bytes = []
    for verb in verbs:
        verb_byte = verb.strip().encode('utf8')
        if verb_byte in this_space.id2row:
            verbs_bytes.append(verb_byte)

    verbs_for_mean_bytes = []
    for verb in verbs_for_mean:
         verb_b = verb.strip().encode('utf8')
         if verb_b in this_space.id2row:
            verbs_for_mean_bytes.append(verb_b)

    print str(len(verbs_bytes)) + ' verbs in main list\n'
    print str(len(verbs_for_mean_bytes)) + ' verbs in mean list\n'

    f_list = io.open(FLAGS.filebase + '/neighbours_list.csv', 'w', encoding='utf8')
    f_mean = io.open(FLAGS.filebase + '/distance_to_mean.csv', 'w', encoding='utf8')

    for verb in verbs_bytes:
        neighbour_list = this_space.get_neighbours(verb, FLAGS.number_neighbours, CosSimilarity())
        neighbour_words = [item[0] for item in neighbour_list]
        neighbour_similarities = [item[1] for item in neighbour_list]
        f_list.write(verb.decode('utf8') + ',')
        f_list.write(','.join(neighbour_words).decode('utf8') + '\n')
        floats_line = 'Sim.,'
        for sim in neighbour_similarities:
            floats_line += '%.7f,' % sim

        verbs_line = 'Verb,'
        for word in neighbour_words:
            if word in verbs_bytes:
                verbs_line += '1,'
            else:
                verbs_line += ','

        f_list.write(floats_line.decode('utf8') + '\n')
        f_list.write(verbs_line.decode('utf8')+'\n')

    f_list.close()

    a = izip(*csv.reader(open(FLAGS.filebase + "/neighbours_list.csv", "rb")))
    csv.writer(open(FLAGS.filebase + "/neighbours_list_tranposed.csv", "wb")).writerows(a)



    verb_ids = [this_space.row2id[verb] for verb in verbs_bytes]
    plot_space_with_verbs(this_space, verb_ids, 300, FLAGS.filebase + '/verbs_and_others.png')
    plot_space_with_verbs(this_space, verb_ids, 0, FLAGS.filebase + '/just_verbs.png')


    verb_rows = dict()

    verb_mean_ids = [this_space.row2id[verb] for verb in verbs_for_mean_bytes]

    len_row = this_space.cooccurrence_matrix.shape[1]
    for verb, index in zip(verbs_for_mean_bytes, verb_mean_ids):
        row = [this_space.cooccurrence_matrix[index,i] for i in xrange(len_row)]
        verb_rows[verb] = row

    mean_row = [0] * len_row

    n_verbs = len(verbs_for_mean_bytes)
    for key in sorted(verb_rows.keys()):
        for i in xrange(len_row):
            mean_row[i] = mean_row[i] + verb_rows[key][i]

    for i in xrange(len_row):
        mean_row[i] = mean_row[i] / n_verbs



    big_neighbour_list = get_neighbours_vector(this_space, numpy.array(mean_row), FLAGS.number_mean_neighbours, CosSimilarity())
    big_neighbour_words = [item[0] for item in big_neighbour_list]
    big_neighbour_similarities = [item[1] for item in big_neighbour_list]

    for word, sim in zip(big_neighbour_words, big_neighbour_similarities):
        f_mean.write(word.decode('utf8') + ',' + '%.7f,' % sim)
        if word in verbs_bytes:
            f_mean.write('1\n'.decode('utf8'))
        else:
            f_mean.write('\n'.decode('utf8'))


    f_mean.close()