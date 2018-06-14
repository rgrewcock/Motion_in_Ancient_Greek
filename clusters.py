import argparse
import os
import io
import time
#import numpy as np
import seaborn as sns
import sklearn.cluster as cluster
import hdbscan


from composes.utils import io_utils


import matplotlib.pyplot as plt

#sns.set_context('poster')
sns.set_color_codes()
plot_kwds = {'alpha' : 0.25, 's' : 80, 'linewidths':0}



def cluster_and_plot(sp, filestem, algo, n_clusters_request, n_dim, n_points_cluster, verb_ids, n_plot, mcs, min_samples, met):
#    n_plot = 1200

    clusterids = [i for i in xrange(n_points_cluster)]
    clusterids.extend(verb_ids)

    #To remove duplicates
    clusterids = list(set(clusterids))

    mat = sp.cooccurrence_matrix.mat
    mat = mat[clusterids,:n_dim]


    if 'kmean' in algo:
        clusterer = cluster.KMeans(n_clusters=n_clusters_request, n_init=50)
    else:
        if met == 1:
            clusterer = hdbscan.HDBSCAN(min_cluster_size=mcs, min_samples = min_samples, algorithm='generic', metric='cosine')
        else:
            clusterer = hdbscan.HDBSCAN(min_cluster_size=mcs, min_samples = min_samples, metric='euclidean')

    clusterer.fit(mat)
    cluster_labels = clusterer.labels_

    ids = [i for i in xrange(n_plot)]
    ids.extend(verb_ids)
    ids = list(set(ids))

    labels = [sp.id2row[i].decode('utf-8') for i in ids]

    ids_for_shortened_mat = [clusterids.index(i) for i in ids]

    nclusters = cluster_labels.max()

    cluster_words_plot = [None]*nclusters
    cluster_words_all = [None]*nclusters
    for i in xrange(nclusters):
        cluster_words_plot[i] = [sp.id2row[j].decode('utf-8') for j in ids
                      if cluster_labels[clusterids.index(j)] == i]
        cluster_words_all[i] = [sp.id2row[j].decode('utf-8') for j in clusterids
                      if cluster_labels[clusterids.index(j)] == i]


    palette = sns.hls_palette(nclusters+1, l=.6, s=.8)
    colors = [palette[x] if x >= 0 else (0.0, 0.0, 0.0) for x in cluster_labels]

    verb_ids_shortened = ids_for_shortened_mat[n_plot:]
    verb_clusters = [cluster_labels[i] for i in verb_ids_shortened]

    if 'kmean' in algo:
        n_verb_clusters = len(set(verb_clusters))
        n_total_clusters = len(set(cluster_labels))
    else:
        n_verb_clusters = len(set(verb_clusters)) - 1
        n_total_clusters = len(set(cluster_labels)) - 1




    if n_total_clusters > 2 and n_verb_clusters < 20:
        print 'Total clusters is ' + str(n_total_clusters) + ', verb clusters is ' + str(n_verb_clusters) + ' so plotting'

        plt.ioff()
        fig = plt.figure(figsize=(25, 17))
        for i, i_cluster, label in zip(ids, ids_for_shortened_mat, labels):
            x = mat[i_cluster,0]
            y = mat[i_cluster,1]
            plt.scatter(x, y, c=colors[i_cluster])#, **plot_kwds)
            plt.annotate(
                    label,
                    xy = (x, y),
                    xytext=(5,2),
                    textcoords='offset points',
                    ha='right',
                    va='bottom')

        plt.autoscale(enable=True,axis='both',tight=True)
        if 'kmean' in algo:
            filebase = filestem
        else:
            filebase = 'clusters/hdbscan/'

        filebase += 'Nverbclusters' + str(n_verb_clusters)
        filebase += 'Nclusters' + str(n_total_clusters)
        filebase += 'Mcs' + str(mcs)
        filebase += 'Minsamps' + str(min_samples)
        if met == 1:
            filebase += 'Cosine'
        else:
            filebase += 'Euclidean'

        filebase += 'Dim' + str(n_dim)
        filebase += 'Points' + str(n_points_cluster)
        filebase += 'Nplot' + str(n_plot)
        filepdf = filebase + '.pdf'
        filecsv = filebase + '.csv'

        f_csv = io.open(filecsv, 'w', encoding='utf8')

        f_csv.write('Clusters: top {:d} words plus verbs only,,,\n'.format(n_plot).decode('utf-8'))
        for cluster_list in cluster_words_plot:
            out_unicode = ','.join(cluster_list) + '\n'.decode('utf-8')
            f_csv.write(out_unicode)

        f_csv.write('\n\nClusters: All words,,,\n'.format(n_plot).decode('utf-8'))
        for cluster_list in cluster_words_all:
            out_unicode = ','.join(cluster_list) + '\n'
            f_csv.write(out_unicode)

        f_csv.close()


        plt.savefig(filepdf, bbox_inches='tight')
        plt.close(fig)
    else:
        print 'Not plotting: total clusters is ' + str(n_total_clusters) + ', verb clusters is ' + str(n_verb_clusters)



    return [clusterer, mat, clusterids, verb_clusters, ids_for_shortened_mat, cluster_words_plot, cluster_words_all]

def run_many_clusters(algo):
    verbs_filename = 'verbs3.txt'

    filelist = ['output_1000BCto500BC_vocab10000_window1_withoutprep',
                'output_499BCto250BC_vocab10000_window1_withoutprep',
                'output_249BCto0AD_vocab10000_window1_withoutprep',
                'output_1ADto250AD_vocab10000_window1_withoutprep',
                'output_251ADto500AD_vocab10000_window1_withoutprep'
            ]

    if 'kmean' in algo:
        f_log = io.open('clusters/kmeans/generallog.csv','w',encoding='utf8')
    else:
        f_log = io.open('clusters/log2.csv', 'w', encoding='utf8')
        f_log.write('n_verb_clusters, n_total_clusters, n_verbs, min_cluster_size, min_samples, metric, dimensions, n_words, n_plot\n'.decode('utf8'))

    for filebase in filelist:
        pickles = [f for f in os.listdir(filebase) if f.endswith('.pkl')]

        if(len(pickles) == 0):
            print 'No pickles found in directory ' + FLAGS.filebase + '!'
            exit()

        pickle = pickles[0]
        fname = filebase + '/' + pickle
        sp = io_utils.load(fname)

        f_verbs = io.open(verbs_filename, 'r', encoding='utf8')
        verbs = list(f_verbs)
        f_verbs.close()

        verbs_bytes = []
        for verb in verbs:
            verb_byte = verb.strip().encode('utf8')
            if verb_byte in sp.id2row:
                verbs_bytes.append(verb_byte)

        print str(len(verbs_bytes)) + ' verbs in main list\n'

        verb_ids = [sp.row2id[verb] for verb in verbs_bytes]

        n_plot = 400

        if 'kmean' in algo:
            for n_words in xrange(3000,3001,1000):
                for dimensions in xrange(2,3):
                    for n_clusters in xrange(8,9):
                        start_time = time.time()
                        [clusterer,
                        mat,
                        clusterids,
                        verb_clusters,
                        ids_for_shortened_mat,
                        cluster_words_plot,
                        cluster_words_all] = cluster_and_plot(sp,
                            'clusters/kmeans/' + verbs_filename[:-4] + filebase[7:-31] + 'Rectangular25',
                            'kmean',
                            n_clusters,
                            dimensions,
                            n_words,
                            verb_ids,
                            n_plot,
                            0,
                            0,
                            0)

                        n_verbs = len(verb_clusters)
                        n_verb_clusters = len(set(verb_clusters))
                        n_total_clusters = len(set(clusterer.labels_)) - 1
                        print str(n_verbs) + ' verbs specified, split into ' + str(n_verb_clusters) + ' clusters.'

                        out_list_str = ['{:4d}'.format(n_verb_clusters),
                                        '{:4d}'.format(n_total_clusters),
                                        '{:3d}'.format(n_verbs),
                                        '{:3d}'.format(dimensions),
                                        '{:5d}'.format(n_words),
                                        '{:4d}'.format(n_plot)]
                        out_str = ','.join(out_list_str)

                        f_log.write(out_str.decode('utf8')+'\n')
                        end_time = time.time()
                        print 'Clustering took {:.2f} s'.format(end_time - start_time)


        else:
            for n_words in xrange(2000,4001,1000):
                for dimensions in xrange(2,8):
                    for min_cluster_size in xrange(15,30):
                        for min_samples in xrange(1,15):
                            for metric in xrange(0,1):
                                start_time = time.time()
                                [clusterer,
                                 mat,
                                 clusterids,
                                 verb_clusters,
                                 ids_for_shortened_mat] = cluster_and_plot(sp,
                                     dimensions,
                                     n_words,
                                     verb_ids,
                                     n_plot,
                                     min_cluster_size,
                                     min_samples,
                                     metric
                                     )

                                n_verbs = len(verb_clusters)
                                n_verb_clusters = len(set(verb_clusters)) - 1
                                n_total_clusters = len(set(clusterer.labels_)) - 1
                                print str(n_verbs) + ' verbs specified, split into ' + str(n_verb_clusters) + ' clusters.'

                                out_list_str = ['{:4d}'.format(n_verb_clusters),
                                                '{:4d}'.format(n_total_clusters),
                                                '{:3d}'.format(n_verbs),
                                                '{:3d}'.format(min_cluster_size),
                                                '{:3d}'.format(min_samples),
                                                '{:2d}'.format(metric),
                                                '{:3d}'.format(dimensions),
                                                '{:5d}'.format(n_words),
                                                '{:4d}'.format(n_plot)]
                                out_str = ','.join(out_list_str)

                                f_log.write(out_str.decode('utf8')+'\n')
                                end_time = time.time()
                                print 'Clustering took {:.2f} s'.format(end_time - start_time)

    f_log.close()

    #return [clusterer, mat, clusterids, verb_clusters]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
#    parser.add_argument('filebase',
#            type=str,
#            help='Name of folder containing data'
#            )
#    parser.add_argument('verbs_filename',
#            type=str,
#            help='Name of file containing list of verbs to use'
#            )
#    parser.add_argument('verbs_for_mean_filename',
#            type=str,
#            help = 'Name of file with restricted set of verbs'
#            )
#    parser.add_argument('-nn','--number_neighbours',
#            type=int,
#            default=200,
#            help='Number of neighbours to output in neighbours_list.csv'
#            )
#
    parser.add_argument('-nmn','--number_mean_neighbours',
            type=int,
            default=1500,
            help='Number of neighbours to output in distance_to_mean.csv'
            )


    FLAGS, unparsed = parser.parse_known_args()

    FLAGS.filebase = 'output_499BCto250BC_vocab10000_window1_withoutprep'
    FLAGS.verbs_filename = 'verbs_fewer_compounds.txt'

    pickles = [f for f in os.listdir(FLAGS.filebase) if f.endswith('.pkl')]

    if(len(pickles) == 0):
        print 'No pickles found in directory ' + FLAGS.filebase + '!'
        exit()

    pickle = pickles[0]
    fname = FLAGS.filebase + '/' + pickle
    sp = io_utils.load(fname)

    f_verbs = io.open(FLAGS.verbs_filename, 'r', encoding='utf8')
    verbs = list(f_verbs)
    f_verbs.close()

    verbs_bytes = []
    for verb in verbs:
        verb_byte = verb.strip().encode('utf8')
        if verb_byte in sp.id2row:
            verbs_bytes.append(verb_byte)

    print str(len(verbs_bytes)) + ' verbs in main list\n'

    verb_ids = [sp.row2id[verb] for verb in verbs_bytes]


