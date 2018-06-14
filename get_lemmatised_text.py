# -*- coding: utf-8 -*-
"""


"""

from bs4 import BeautifulSoup

this_file_path = os.path.dirname(__file__)

# This is a hardcoded relative path which needs pointing to the folder with all of the Diorisis
# .xml files
Diorisis_folder = os.path.join(this_file_path, "../../Diorisis")


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


def read_file(filename):
    f1 = open(filename,'r',encoding='utf8')
    f1s = f1.read()
    soup = BeautifulSoup(f1s,'lxml')
    f1.close()
    sentences = soup.find_all('sentence')
    age = soup.find('creation').find('date').get_text()
    return [sentences, age]

def write_lemmas_file(filebase, with_punct):
    [sentences, age] = read_file(filebase + '.xml')

    if with_punct:
        out_filename = filebase + ' lemmas with punct.txt'
    else:
        out_filename = filebase + ' lemmas no punct.txt'

    f = open(out_filename, 'w', encoding='utf8')

    for sentence in sentences:
        lemmatised = get_full_sentence_lemmas(sentence, with_punct)
        print(lemmatised, file = f)

    f.close()



if __name__ == "__main__":
    print('Hello!')



