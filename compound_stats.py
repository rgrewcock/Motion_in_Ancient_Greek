import shutil
import os
import re

this_file_path = os.path.dirname(__file__)

# This is a hardcoded relative path which needs pointing to the folder with all of the Diorisis
# processed data in (ie the "textname lemmas nopunct.txt" files)
Diorisis_folder = os.path.join(this_file_path, "../../Diorisis/")

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

def get_verb_list(filename):
    f = open(filename, 'r', encoding='utf8')
    verbs = f.read().splitlines()
    f.close()
    return verbs

def get_all_verb_lists():
    allfiles = os.listdir()
    files = [ fname for fname in allfiles if fname.endswith('.vbs')]
    verb_lists = dict()
    for file in files:
        verb_lists[file[:-4]] = get_verb_list(file)

    return verb_lists

def make_age_files(start, stop, step):
    for firstyear in range(start, stop, step):
        endyear = firstyear + step - 1
        make_file_with_ages(make_filename_from_ages(firstyear, endyear), firstyear, endyear)

def get_occurrences_in_file(txtfile, verb_list, verb_name):
    with open(txtfile, 'r', encoding='utf8') as f:
        content = f.read()

    outfile = open(txtfile[:-4] + '_' + verb_name + '.occ', 'w', encoding='utf8')
    n_occurrences = dict()
    for verb in verb_list:
        matches = re.findall('\s' + verb + '\s', content)
        n_occurrences[verb] = len(matches)
        matches = [m.strip() for m in matches]
        if len(matches) > 0:
            outfile.write(','.join(matches) + '\n')

    outfile.close()
    return n_occurrences

def get_all_occurrences():
    allfiles = os.listdir()
    contentfiles = [fname for fname in allfiles if fname.endswith('.txt')]
    verb_lists = get_all_verb_lists()
    main_verbs = sorted(verb_lists.keys())
    main_verbs_doubled = []
    for v in main_verbs:
        main_verbs_doubled.append(v)
        main_verbs_doubled.append('compounds of ' + v)

    f_summary = open('summary.csv', 'w', encoding='utf8')
    all_data = dict()
    f_summary.write('Age,' + ','.join(main_verbs_doubled) + '\n')
    for file in contentfiles:
        f_detail = open(file[:-4] + '_detail.csv', 'w', encoding='utf8')
        f_summary.write(file[:-4] + ',')
        d = dict()
        for main_verb_beta in main_verbs:
            verb_list = verb_lists[main_verb_beta]
            occ_dict = get_occurrences_in_file(file, verb_list, main_verb_beta)
            counts = [occ_dict[verb_list[i]] for i in range(0,len(verb_list))]
            f_summary.write(str(occ_dict[verb_list[0]]) + ',')
            f_summary.write(str(sum(counts[1:])) + ',')

            f_detail.write(','.join(verb_list) + '\n')
            f_detail.write(','.join([str(c) for c in counts]) + '\n')
            d[main_verb_beta] = occ_dict
        f_summary.write('\n')
        all_data[file[:-4]] = d

        f_detail.close()
    f_summary.close()

    return all_data

if __name__ == "__main__":
    print('hello')
