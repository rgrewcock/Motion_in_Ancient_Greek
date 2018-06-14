#from composes.semantic_space.space import Space

import argparse
import os

from composes.utils import io_utils


import matplotlib.pyplot as plt


def plot_with_labels(co_matrix, labels, filename):
  assert co_matrix.shape[0] >= len(labels), 'More labels than embeddings'
  plt.figure(figsize=(20, 20))  # in inches
  for i, label in enumerate(labels):
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


def plot_space(this_space, n_plot, filename):
    labels = [this_space.id2row[i].decode('utf-8') for i in xrange(n_plot)]
    plot_with_labels(this_space.cooccurrence_matrix, labels, filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
            'filebase',
            type=str,
            help='Name of folder containing data')
    parser.add_argument(
            '--nplot',
            type=int,
            default=300,
            help='Number of points to include in plot')
    parser.add_argument(
            '--nSVD',
            type=int,
            default=200,
            help='Number of dimensions used for SVD')
    parser.add_argument(
            '--normalisation',
            type=str,
            default = '0',
            help = 'Type of normalisation'
        )

    FLAGS, unparsed = parser.parse_known_args()

    #This needs pointing to the location that DISSECT is installed to.
    build_core_str = 'python C:/Users/Rachel/Documents/dissect-master/dissect-master/src/pipelines/build_core_space.py '
    build_core_str += ' -i ' + FLAGS.filebase + '/sparsematrix'
    build_core_str += ' --input_format sm --w ppmi -r svd_' + str(FLAGS.nSVD)  + ' -o ' + FLAGS.filebase
    if FLAGS.normalisation != '0':
        build_core_str += ' -n all'

    print build_core_str
    os.system(build_core_str)

    saved_space_filename = FLAGS.filebase + "/CORE_SS.sparsematrix.ppmi.svd_" \
            + str(FLAGS.nSVD)

    if FLAGS.normalisation != '0':
        saved_space_filename += ".all"

    saved_space_filename += ".pkl"

    this_space = io_utils.load(saved_space_filename)

    plot_space(this_space, FLAGS.nplot, FLAGS.filebase + ".png")