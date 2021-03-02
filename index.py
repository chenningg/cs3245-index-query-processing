#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os

ps = nltk.stem.PorterStemmer()


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -i directory-of-documents -d dictionary-file -p postings-file"
    )


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("indexing...\n")
    # This is an empty method
    # Pls implement your code in below

    # We'll be implementing BSBI.

    dictionary = (
        {}
    )  # holding variable of format dictionary = {'term': {"docFreq": i, "termID": j, "postingListPointer": k}, ... }
    postingLists = []  # holding variable of format postingList = [ list1, list2, ... ]
    termID = 0  # running integer for termID assignment, starting from zero
    docIDs = os.listdir(in_dir)  # read in paths of all documents in the in_dir

    # subset of paths for testing purposes
    docIDs = docIDs[:10]

    # process every document
    for docID in docIDs:
        f = open(os.path.join(in_dir, docID), "r")  # open the document file
        text = f.read()  # read the document in fulltext
        text = text.lower()  # convert text to lower case
        sentences = nltk.sent_tokenize(text)  # tokenize by sentence
        for sentence in sentences:
            words = nltk.word_tokenize(sentence)  # tokenize by word
            words_stemmed = [ps.stem(w) for w in words]  # stem every word
            for word in words_stemmed:
                if word not in dictionary:  # new word/term, add to dictionary
                    dictionary[word] = {
                        "docFreq": 1,
                        "termID": termID,
                        "postingListPointer": termID,
                    }  # postingListPointer same as termID for now
                    postingLists.append([docID])
                    termID += 1
                else:  # word is in dictionary
                    if (
                        docID
                        not in postingLists[dictionary[word]["postingListPointer"]]
                    ):  # check if docID already in the corresponding postingList
                        postingLists[dictionary[word]["postingListPointer"]].append(
                            docID
                        )  # append docID to end of corresponding postingList if not exists
                        dictionary[word]["docFreq"] += 1

    print(dictionary)
    print(termID)
    print(postingLists)
    print(dictionary["and"])


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:d:p:")
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-i":  # input directory
        input_directory = a
    elif o == "-d":  # dictionary file
        output_file_dictionary = a
    elif o == "-p":  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if (
    input_directory == None
    or output_file_postings == None
    or output_file_dictionary == None
):
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
