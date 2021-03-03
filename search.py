#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle


# higher number indicates lower precendence --> i.e. when checking for precedence, we can do
#       PRECEDENCE["OR"] > PRECEDENCE["()"] --> FALSE, meaning "OR" has lower precendence than ()
PRECEDENCE = {
    "()": 4,
    "NOT": 3,
    "AND": 2,
    "OR": 1

}

def parse_query():
    
    parsed_query = ""
    return parsed_query


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    
    ''' ==================================================================
    load in entire dictionary.txt
    underlying assumption - dictionary is relatively small, the posting list is the large one
    ================================================================== ''' 
    f_dict = open(
        os.path.join(os.path.dirname(__file__), dict_file), "rb"
    )
    
    dictionary = pickle.load(f_dict)


    ''' ==================================================================
    load in entire queries.txt
    save as a list, strip encoding
    ================================================================== ''' 
    f_queries = open(
        os.path.join(os.path.dirname(__file__), queries_file), "rb"
    )
    
    queries = [query.decode() for query in f_queries.read().splitlines()]



    
    ''' ==================================================================
    save out to results.txt
    just overwrite the entire file 
    ================================================================== ''' 
    f_results = open(
        os.path.join(os.path.dirname(__file__), results_file), 'w'
    )
    
    results = [[12, 40, 45], [], [123, 456]]
    
    for result in results:
        if len(result) == 0:
            f_results.write("\n")    
        else:
            listToStr = ' '.join([str(doc_id) for doc_id in result])
            
            f_results.write(f"{listTo}\n")
        
        f_results.write(line)
        f_results.write("\n")
    
    f_results.close()

    f_results = open(
        os.path.join(os.path.dirname(__file__), results_file), 'r'
    )

    queries = [query for query in f_results.read().splitlines()]
    


    # This is an empty method
    # Pls implement your code in below

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
