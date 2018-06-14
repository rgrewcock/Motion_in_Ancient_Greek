# -*- coding: utf-8 -*-
"""


"""

from bs4 import BeautifulSoup
import os

import shelve

DL_folder = 'C:\\Users\\Rachel\\Documents\\greekutils\\PerseusDL_lemmatised_corpus\\AGCorpus'

class Adverb_data(object):

    def __init__(self,date,filename,sentence_id,sentence_location,word_id,adverb_form,adverb_lemma):
        self.date = date
        self.filename = filename
        self.sentence_id = sentence_id
        self.sentence_location = sentence_location
        self.word_id = word_id
        self.adverb_form = adverb_form
        self.adverb_lemma = adverb_lemma

    def briefprint(self):
        ret_str = 'Sentence in {0}, at location {1} and id {2} is:\n'.format(self.filename, self.sentence_location, self.sentence_id) \
                + '{0}\n'.format(self.full_sentence_beta) 

        for (verb_lemma, verb_form, distance_after) in zip(self.verb_lemma_list, self.verb_form_list, self.distance_after_list):
            ret_str += 'Verb {0} ({1}) is {2} words after {3} ({4})\n'.format(verb_form, verb_lemma, distance_after, self.adverb_form, self.adverb_lemma)

        return ret_str

    def longprint(self):
        ret_str = 'Sentence in {0}, at location {1} and id {2} is:\n'.format(self.filename, self.sentence_location, self.sentence_id) \
                + '{0}\n'.format(self.full_sentence_beta)
        ret_str += 'Punct marks are: '
        for mark in self.punct_mark_list:
            ret_str += mark + ' '
        ret_str += '\n'
        ret_str +='Lemmas are: \n{0}\n'.format(self.full_sentence_lemmas)

        for (verb_lemma, verb_form, verb_analyses, distance_after) in zip(self.verb_lemma_list, self.verb_form_list, self.verb_analysis_list, self.distance_after_list):
            ret_str += 'Verb {0} ({1}) is {2} words after {3} ({4})\n'.format(verb_form, verb_lemma, distance_after, self.adverb_form, self.adverb_lemma)
            for analysis in verb_analyses:
                ret_str += '    Analysis: {0}\n'.format(analysis)
            
        return ret_str
    
class Verb_data(object):
    #NB: Various of the equivalent fields in Eis_data are strings, here we convert them to ints.
    def __init__(self,date,filename,sentence_id,sentence_location,full_sentence_beta,full_sentence_lemmas,adverb_word_id,adverb_form,adverb_lemma,\
        verb_distance_after,verb_form,verb_lemma,verb_analyses_list):
        self.date = int(date)
        self.filename = filename
        self.sentence_id = int(sentence_id)
        self.sentence_location = sentence_location
        self.full_sentence_beta = full_sentence_beta
        self.full_sentence_lemmas = full_sentence_lemmas
        self.adverb_word_id = int(adverb_word_id)
        self.adverb_form = adverb_form
        self.adverb_lemma = adverb_lemma
        self.verb_distance_after = verb_distance_after
        self.verb_form = verb_form
        self.verb_lemma = verb_lemma
        self.verb_analyses_list = verb_analyses_list
        
    def briefprint(self):
        ret_str = 'Sentence in {0} (written {1} AD), at location {2} and id {3} is:\n'.format(self.filename, self.date, self.sentence_location, self.sentence_id) \
                + '{0}\n'.format(self.full_sentence_beta) \
                + 'Verb {0} ({1}) is {2} words after {3} ({4})\n'.format(self.verb_form, self.verb_lemma, self.verb_distance_after, self.adverb_form, self.adverb_lemma)
        return ret_str

    def longprint(self):
        ret_str = 'Sentence in {0} (written {1} AD), at location {2} and id {3} is:\n'.format(self.filename, self.date, self.sentence_location, self.sentence_id) \
                + '{0}\n'.format(self.full_sentence_beta) \
                + 'Lemmas are:\n' \
                + '{0}\n'.format(self.full_sentence_lemmas) \
                + 'Verb {0} ({1}) is {2} words after {3} ({4})\n'.format(self.verb_form, self.verb_lemma, self.verb_distance_after, self.adverb_form, self.adverb_lemma)
        for verb_analysis in self.verb_analyses_list:
            ret_str += '    Analysis: {0}\n'.format(verb_analysis)
        
        return ret_str
 
    
def print_csv(inst):
    ret_str = '{0}£"{1}"£"{2}"£"{3}"£{4}££'.format(inst.date, inst.verb_lemma, inst.verb_form, inst.adverb_form, inst.verb_distance_after)
    ret_str += '"{0}"£"{1}"£"{2}"£"{3}"£"{4}"'.format(inst.full_sentence_beta, inst.full_sentence_lemmas, inst.filename, inst.sentence_id, inst.sentence_location)

    return ret_str
    
def load_adverb_data():
    os.chdir(DL_folder)
    db = shelve.open('bigdict_adverbs.she')
    adverb_data_dict = db['big_dict']
    db.close()
    return adverb_data_dict

def write_adverb_data(adverb_data):
    os.chdir(DL_folder)
    db = shelve.open('bigdict_adverbs.she')
    db['big_dict'] = adverb_data
    db.close()

def get_verbs_within_range_of_adverbs(min_before, max_after):
    #If "distance_after" is >= min_before and <= max_after, add to list of verbs and return
    verb_list = []
    adverb_keys = list(adverb_data_dict.keys())
    adverb_keys = [x for x in adverb_keys if len(adverb_data_dict[x]) > 0]
    adverb_keys.sort(key = lambda x: int(adverb_data_dict[x][0].date))
    
    for text_name in adverb_keys:
        adverb_list = adverb_data_dict[text_name]
        if(len(adverb_list)):
            date = adverb_list[0].date
        for inst in adverb_list:
            punct_rel_id_list = [x - int(inst.word_id) for x in inst.punct_id_list]
            for (distance_after, verb_form, verb_lemma, verb_analyses) in \
            zip(inst.distance_after_list, inst.verb_form_list, inst.verb_lemma_list, inst.verb_analysis_list):
                punct_in_between = 0 
                if(min_before <= distance_after <= max_after):
                    for punct in punct_rel_id_list:
                        if distance_after < punct < 0:
                            punct_in_between = 1
                        if 0 < punct < distance_after:
                            punct_in_between = 1
                    if punct_in_between == 0:
                        verb_list.append(Verb_data(date,text_name,inst.sentence_id,inst.sentence_location,inst.full_sentence_beta, \
                                    inst.full_sentence_lemmas, inst.word_id, inst.adverb_form, inst.adverb_lemma, \
                                    distance_after,verb_form,verb_lemma,verb_analyses))
        print('Parsed text ' + text_name)
    return verb_list


def get_sorted_verbs(min_before, max_after):
    all_verb_instances = get_verbs_within_range_of_adverbs(min_before, max_after)
    f_summary_name = 'SummaryAdverbsOfVerbsBetween{0}And{1}.txt'.format(min_before,max_after)
    f_all_name = 'InstancesAdverbsOfVerbsBetween{0}And{1}.txt'.format(min_before,max_after)
    f_verbs_name = 'ListAdverbsOfVerbsBetween{0}And{1}.txt'.format(min_before,max_after)
    f_psv_name = 'InstancesAdverbsOfVerbsBetween{0}And{1}.csv'.format(min_before, max_after)
    f_summary = open(f_summary_name, 'w', encoding='utf8')
    f_all = open(f_all_name, 'w', encoding='utf8')
    f_verbs = open(f_verbs_name, 'w', encoding='utf8')
    f_psv = open(f_psv_name, 'w', encoding = 'utf8')


    verb_dict = dict()
    for inst in all_verb_instances:
        if inst.verb_lemma not in verb_dict:
            verb_dict[inst.verb_lemma] = []
        verb_dict[inst.verb_lemma].append(inst)

    distinct_verbs = sorted(list(verb_dict.keys()))
    for verb_lemma in distinct_verbs:
        lem_instances = verb_dict[verb_lemma]
        dates = sorted(list(set([inst.date for inst in lem_instances])))
        print('Verb {0} is seen within {1}:{2} of adverbs:'.format(verb_lemma, min_before, max_after), file=f_summary)
        print('Verb {0} is seen within {1}:{2} of adverbs:\n'.format(verb_lemma, min_before, max_after), file=f_all)
        for date in dates:
            date_instances = [inst for inst in lem_instances if inst.date == date]
            print('    {0} AD: {1} instances'.format(date, len(date_instances)), file = f_summary)
            print('    {0} AD: {1} instances:\n'.format(date, len(date_instances)), file = f_all)
            for inst in date_instances:
                print(inst.longprint(),file=f_all)
                print(print_csv(inst),file=f_psv)

        print('\n',file=f_summary, end='')
        print('\n',file=f_all, end = '')
        print(verb_lemma, file = f_verbs)

    f_summary.close()
    f_all.close()
    f_verbs.close()
    f_psv.close()

    return verb_dict



def write_adverb_file(filename, adverb_list):
    f = open(filename, 'w', encoding='utf8')

    for instance in adverb_list:
        print(instance.longprint(), file=f)

    f.close()

def get_full_sentence_beta(sentence):
    l = []
    word_or_puncts = sentence.find_all(['word','punct'])
    for word_or_punct in word_or_puncts:
        if(word_or_punct.has_attr('form')):
            l.append(' ' + word_or_punct['form'])
        if(word_or_punct.has_attr('mark')):
            l.append(word_or_punct['mark'])

    return ''.join(l)

def get_full_sentence_lemmas(sentence):
    l = []
    lemma_or_puncts = sentence.find_all(['lemma','punct'])
    for lemma_or_punct in lemma_or_puncts:
        if(lemma_or_punct.has_attr('entry')):
            l.append(' ' + lemma_or_punct['entry'])
        if(lemma_or_punct.has_attr('mark')):
            l.append(lemma_or_punct['mark'])
    
    return ''.join(l)

def get_verbs(words):
    verb_lemma_list = []
    verb_form_list = []
    verb_analysis_list = []
    verb_id_list = []
    for word in words:
        lemma = word.find('lemma')
        morphs = []
        pos = ''
        if(lemma.has_attr('pos')):
            pos = lemma['pos']
        if(lemma.has_attr('POS')):
            pos = lemma['POS']
        if pos == "verb":
            analyses = word.find_all('analysis')
            for a in analyses:
                morphs.append(a['morph'])
            
            verb_analysis_list.append(morphs)
            verb_id_list.append(int(word['id']))
            verb_lemma_list.append(lemma['entry'])
            verb_form_list.append(word['form'])

    return verb_lemma_list, verb_form_list, verb_analysis_list, verb_id_list

def get_adverb_data(sentences, adverbs, age, filename_base, filename_out):
    adverb_data = list()
    for sentence in sentences:
        sentence_id = sentence['id']
        sentence_location = sentence['location']
        words = sentence.find_all('word')
        word_or_puncts = sentence.find_all(['word','punct'])

        [verb_lemmas, verb_forms, verb_analyses, verb_ids] = get_verbs(words)

        save_sentence = 0
        for word in words:
            if(word['form'] in adverbs):
                save_sentence = 1

        punct_id_list = []
        punct_mark_list = []
        last_id = 0
        if save_sentence == 1:
            for wop in word_or_puncts:
                if wop.name == 'punct' and wop.has_attr('mark'):
                    punct_id_list.append(last_id + 0.5)
                    punct_mark_list.append(wop['mark'])
                if wop.name == 'word' and wop.has_attr('id'):
                    last_id = int(wop['id'])
        
        for word in words:
            if(word['form'] in adverbs):
                lemma = word.find('lemma')
                new_inst = Adverb_data(age, filename_base, sentence_id, sentence_location, \
                                       word['id'], word['form'], lemma['entry'])
                new_inst.full_sentence_beta = get_full_sentence_beta(sentence)
                new_inst.full_sentence_lemmas = get_full_sentence_lemmas(sentence)
                new_inst.verb_lemma_list = verb_lemmas
                new_inst.verb_form_list = verb_forms
                new_inst.verb_analysis_list = verb_analyses
                new_inst.distance_after_list = [x - int(word['id']) for x in verb_ids]
                new_inst.punct_id_list = punct_id_list
                new_inst.punct_mark_list = punct_mark_list
                adverb_data.append(new_inst)

    write_adverb_file(filename_out, adverb_data)
    return adverb_data
    
def read_file(filename):
    f1 = open(filename,'r',encoding='utf8')
    f1s = f1.read()
    soup = BeautifulSoup(f1s,'lxml')
    f1.close()
    sentences = soup.find_all('sentence')
    age = soup.find('creation').find('date').get_text()
    return [sentences, age]

def read_lemma_corpus_get_adverb_data():
    os.chdir(DL_folder)
    DL_files = os.listdir()

    adverb_dict = dict()

    adverbs = ['h(me/ras','h(merw=n','nuktw=n','nukto/s','meshmbri/as','dei/lhs','e(spe/ras','qe/rous','xeimw=nos','h(=ros','o)pw/ras',\
                'loipou=','mhno/s','mhnw=n','w(/ras','w(ra/wn','qe/reos','e)/tous','e)/teos','e)te/wn', 'e)nto\s', 'xro/nw|', 'xro/nou']
    
    for DL_file in DL_files:
        if(DL_file.endswith('.xml')):
            print('Loading ' + DL_file) 
            [sentences, age] = read_file(DL_file)
            filename_base = DL_file[:-4]
            filename_out = filename_base + ' adverb_data.txt'
            adverb_dict[filename_base] = get_adverb_data(sentences, adverbs, age, filename_base, filename_out)
            print('{0} instances saved'.format(len(adverb_dict[filename_base])))
    return adverb_dict

if __name__ == "__main__":
    adverb_data_dict = load_adverb_data()
    print('Hello!')
    

    
