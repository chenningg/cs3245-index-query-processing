#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle


def parse():
    parsed_query = ""
    return parsed_query

def shunting_yard():
    operators = ["NOT", "AND", "OR", "ANDNOT"]
    operator_precedence = {"NOT": 2, "AND": 1, "ANDNOT": 1, "OR": 0}



def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    
    # This is an empty method
    # Pls implement your code in below

    
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
    for every query, parse it properly
    then query against the dictionary and posting file
    posting file will be accessed through pointers only, and never loaded fully into memory
    append the solution to results (list of lists)
    ================================================================== ''' 
    f_postings = open(
        os.path.join(os.path.dirname(__file__), postings_file), "rb"
    )    
    
    results = []

    for query in queries:
        # make sure the query is well-formed first
        parsed_query = parse(query)

        # holding variable for the posting lists that we will get
        posting_lists = []
        
        # query against the dictionary + posting list to get the necessary posting list


        # perform the required intersection/merge on posting_lists




    
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
            result_string = ' '.join([str(doc_id) for doc_id in result])
            result_string = result_string.strip()
            f_results.write(f"{result_string}\n")
    

    ''' ==================================================================
    close out all files
    ================================================================== ''' 
    f_dict.close()
    f_queries.close()
    f_postings.close()
    f_results.close()

    # # to check the output in code
    # f_results = open(
    #     os.path.join(os.path.dirname(__file__), results_file), 'r'
    # )

    # queries = [query for query in f_results.read().splitlines()]
    # print(queries)
    



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
