#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle

ps = nltk.stem.PorterStemmer()

# Store valid operators as well as their precedence level (higher is more precendent)
OPERATORS = ["NOT", "AND", "OR", "ANDNOT"]
OPERATOR_PRECEDENCE = {"NOT": 2, "AND": 1, "ANDNOT": 1, "OR": 0}


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
    )


# Parses a query into proper notation for shunting yard algorithm to process
def parse(query):
    # Split by spaces in the query to extract terms
    raw_tokens = query.split(" ")  # Tokens before processing
    tokens = []  # Tokens in query after processing

    # Need to get brackets in query out because they do not have spaces (no nested brackets)
    for raw_token in raw_tokens:
        token_term = raw_token  # Term within the parenthesis, if any
        end_parenthesis_count = 0  # Keep track of closing brackets
        if raw_token[0] == "(":
            tokens.append("(")  # Add parenthesis to operator stream
            token_term = token_term[1:]

        # If there are end brackets, need to add term before bracket
        if raw_token[-1] == ")":
            end_parenthesis_count += 1
            token_term = token_term[:-1]
        if end_parenthesis_count > 0:
            tokens.append(token_term)
            tokens.append(")")
        else:
            tokens.append(token_term)

    return shunting_yard(query, tokens)


# Shunting yard algorithm to get reverse polish notation of query
def shunting_yard(query, tokens):
    # Check if we can combine AND NOT into ANDNOT
    def is_andnot(token):
        return tokens and token == "AND" and tokens[0] == "NOT"

    # Define output queue and operator stack
    output_queue = []  # The reverse polish notation output
    operator_stack = []

    # Read in each token
    while tokens:
        token = tokens.pop(0)

        if is_andnot(token):
            token = "ANDNOT"  # Combine the AND and the NOT into ANDNOT
            tokens.pop(0)  # Remove the NOT from the tokens list

        # If token is not an operator nor parenthesis, simply push it to the output queue
        if (token not in OPERATORS) and token != "(" and token != ")":
            # make the token lower case and stem the token so that it will match the dictionary
            output_queue.append(ps.stem(token.lower()))
        # If token is an operator, need to check before pushing to operator stack
        elif token in OPERATORS:
            # Check if operator stack is not empty and current operator is smaller in precedence or is right associative
            # If so, push it to the operator stack (because it has smaller precedence). Otherwise, push all operators with precedence smaller than it to the output first.
            while (
                operator_stack
                and operator_stack[-1] != "("
                and (
                    OPERATOR_PRECEDENCE[operator_stack[-1]] > OPERATOR_PRECEDENCE[token]
                    or (
                        OPERATOR_PRECEDENCE[operator_stack[-1]]
                        == OPERATOR_PRECEDENCE[token]
                        and token != "NOT"
                    )
                )
                and operator_stack[-1] != "("
            ):
                output_queue.append(operator_stack.pop())
            operator_stack.append(token)
        # If token is left parenthesis (highest precedence), just push onto operator stack
        elif token == "(":
            operator_stack.append(token)
        # If token is right parenthesis, all encapsulated operators automatically gain highest precedence
        elif token == ")":
            try:
                # While not "(", all preceding operators become of high precedence (encapsulatd in brackets) and are moved to output
                while operator_stack[-1] != "(":  # Will throw error if cannot be found
                    output_queue.append(operator_stack.pop())
                if operator_stack[-1] == "(":
                    operator_stack.pop()  # Discard the "(" since we don't need it in output (already in order)
            except:
                print("Mismatched parenthesis detected for query '{}'.".format(query))
                return []  # Return empty list (error)

    # After while loop, if no more tokens to read, pop all remaining operators to output
    if not tokens:
        while operator_stack:
            # make sure that we do not care about malformed single left bracket queries
            operator = operator_stack.pop()

            if operator == "(":
                print("Mismatched parenthesis detected for query '{}'.".format(query))
                return []
            output_queue.append(operator)

    return output_queue


def get_postings_list(term, dictionary, f_postings):
    try:
        pointer = dictionary[term]["pointer"]  # get pointer value
        f_postings.seek(pointer, 0)  # bring the pointer to the postings_list of term_1
        # read out the associated posting list for the term
        postings_list = pickle.load(f_postings)
    except:
        postings_list = []
    return postings_list  # a postings_list


def skip_pointer_check(value):
    # skip pointers are strings. convert to integer and return to be used as list index
    if isinstance(value, str):
        return int(value[1:])
    # if not skip pointer, we set to none
    else:
        return None


# # Merging algorithm
# def merge_with_skips(postings_list_1, postings_list_2, mode):
#     merged_list = [] # holding list for valid doc_ids
#     skip_marker = '^' # the indicator of a skip pointer
#     curr_index_1 = curr_index_2 = 0 # the index we are on for the respective lists right now
#     skip_pointer_1 = skip_pointer_2 = 0  # which index should we be skipping to next, if possible


#     # while loop ends when we reach the end of both posting lists
#     while (curr_index_1 != len(postings_list_1) and curr_index_2 != len(postings_list_2)):
#         curr_value_1 = postings_list_1[curr_index_1]
#         curr_value_2 = postings_list_2[curr_index_2]

#         # check if current index position is a skip pointer
#         skip_pointer_1 = skip_pointer_check(curr_value_1)
#         skip_pointer_2 = skip_pointer_check(curr_value_2)

#         # if it is indeed a skip pointer, we need to move up one index for actual the current value
#         if skip_pointer_1 != None:
#             curr_index_1 += 1
#             curr_value_1 = postings_list_1[curr_index_1]

#         if skip_pointer_2 != None:
#             curr_index_2 += 1
#             curr_value_2 = postings_list_2[curr_index_2]

#         # perform a comparison of current_values. output the result to merged_list. then decide if we can actually utilise the skip pointer
#         if curr_value_1 == curr_value_2:
#             if mode == "NOT"
#             merged_list


# handle NOT operator
# expect input to be postings_list_1 = results, postings_list_2 = all_doc_ids
# we want the result as [postings_list_2 - postings_list_1]
def query_not(postings_list_1, postings_list_2):
    results = []  # holding list for valid doc_ids
    skip_marker = "^"  # the indicator of a skip pointer

    # the index we are on for the respective lists right now
    curr_index_1 = curr_index_2 = 0

    # which index should we be skipping to next, if possible
    skip_pointer_1 = skip_pointer_2 = 0

    # while loop ends when we reach the end of both posting lists
    while True:
        # terminating conditions
        # as long as postings_list_2 is exhausted, we do not want the rest of postings_list_1
        if curr_index_2 >= len(postings_list_2):
            return results
        # if postings_list_1 is exhausted, the remainder of postings_list_2 will be added into results then returned
        elif curr_index_1 >= len(postings_list_1):
            for value in postings_list_2[curr_index_2:]:
                if skip_pointer_check(value) == None:
                    results.append(value)
            return results

        curr_value_1 = postings_list_1[curr_index_1]
        curr_value_2 = postings_list_2[curr_index_2]

        # check if current index position is a skip pointer
        skip_pointer_1 = skip_pointer_check(curr_value_1)
        skip_pointer_2 = skip_pointer_check(curr_value_2)

        # if it is indeed a skip pointer, we need to move up one index for actual the current value
        if skip_pointer_1 != None:
            curr_index_1 += 1
            curr_value_1 = postings_list_1[curr_index_1]

        if skip_pointer_2 != None:
            curr_index_2 += 1
            curr_value_2 = postings_list_2[curr_index_2]

        # perform a comparison of current_values. output the result to merged_list. then decide if we can actually utilise the skip pointer
        # 1==2 : for NOT postings_list_1, we don't want this
        if curr_value_1 == curr_value_2:
            # move up both indexes and do not add anything to results. cannot skip here!
            curr_index_1 += 1
            curr_index_2 += 1

        # use the standard process that if curr_value_2 is smaller than that of curr_value_1, we append it and then try to advance curr_value_2

        # 1 < 2: we want the value of 2
        elif curr_value_2 < curr_value_1:
            results.append(curr_value_2)

            # move up postings_list_2 value
            # if skip_pointer exists, we check the value to the pointers' right (skip pointers point to other skip pointers)
            if skip_pointer_2 != None:
                # The last skip pointer points to last element in the postings list
                if skip_pointer_2 == len(postings_list_2) - 1:
                    skip_value_2 = postings_list_2[skip_pointer_2]
                # Otherwise, get the value of the posting that the skip pointer points to
                else:
                    skip_value_2 = postings_list_2[skip_pointer_2 + 1]

                # [^4, 1, 2, 3, ^7, 9, 10]
                # append all values prior to the results
                if skip_value_2 <= curr_value_1:
                    results += postings_list_2[curr_index_2 + 1 : skip_pointer_2]

                curr_index_2 = skip_pointer_2 + 1

    return


# handle AND operator
def query_and(term_1, term_2):
    return


# handle OR operator
def query_or(term_1, term_2):
    return


# handle ANDNOT operator
def query_andnot(term_1, term_2):
    return


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print("running search on the queries...")

    # This is an empty method
    # Pls implement your code in below

    """ ==================================================================
    load in entire dictionary.txt
    underlying assumption - dictionary is relatively small, the posting list is the large one
    also load in all document ids for NOT operation
    ================================================================== """
    f_dict = open(os.path.join(os.path.dirname(__file__), dict_file), "rb")
    dictionary = pickle.load(f_dict)

    # also load in all document IDs for NOT operations
    doc_ids_file = "doc_ids"
    f_doc_ids = open(os.path.join(os.path.dirname(__file__), doc_ids_file), "rb")
    all_doc_ids = pickle.load(f_doc_ids)

    """ ==================================================================
    load in entire queries.txt
    save as a list, strip encoding
    ================================================================== """
    f_queries = open(os.path.join(os.path.dirname(__file__), queries_file), "rb")
    queries = [query.decode() for query in f_queries.read().splitlines()]

    """ ==================================================================
    for every query, parse it properly
    then query against the dictionary and posting file
    posting file will be accessed through pointers only, and never loaded fully into memory
    append the solution to results (list of lists)
    ================================================================== """
    f_postings = open(os.path.join(os.path.dirname(__file__), postings_file), "rb")

    results = []

    for query in queries:
        # make sure the query is well-formed first
        parsed_query = parse(query)
        print(query, ":", parsed_query)

        # ['bill', 'gate', 'vista', 'xp', 'OR', 'AND', 'mac', 'ANDNOT', 'OR', 'hello', 'world', 'AND', 'cya', 'AND', 'goodby', 'NOT', 'OR']

        # holding variable for the posting lists that we will get
        results = None
        term_stack = []

        for token in parsed_query:
            # add into our term_stack (basically a stack of words that we are checking against the dictionary)
            if token not in OPERATORS:
                term_stack.append(token)
            # detect an operator
            else:
                # unary operator, applies to one term only
                if token == "NOT":
                    # if no results, find postings_list for the term, assign to results, then do a NOT with all_doc_ids
                    if results == None:
                        term_1 = term_stack.pop()
                        results = get_postings_list(term_1, dictionary, f_postings)

                    # now that results will exist, do a NOT of results with all_doc_ids
                    query_not(results, all_doc_ids)

                # term_stack.pop() if results == None else results

                # # binary operators, applies to two terms
                # elif token == "AND":
                #     query_and(term_stack.pop(), term_stack.pop())
                # elif token == "OR":
                #     query_or(term_stack.pop(), term_stack.pop())
                # elif token == "ANDNOT":
                #     query_andnot(term_stack.pop(), term_stack.pop())
        # query against the dictionary + posting list to get the necessary posting list

        # perform the required intersection/merge on posting_lists

    """ ==================================================================
    save out to results.txt
    just overwrite the entire file 
    ================================================================== """
    f_results = open(os.path.join(os.path.dirname(__file__), results_file), "w")

    for result in results:
        if len(result) == 0:
            f_results.write("\n")
        else:
            result_string = " ".join([str(doc_id) for doc_id in result])
            result_string = result_string.strip()
            f_results.write(f"{result_string}\n")

    """ ==================================================================
    close out all files
    ================================================================== """
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
    opts, args = getopt.getopt(sys.argv[1:], "d:p:q:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-d":
        dictionary_file = a
    elif o == "-p":
        postings_file = a
    elif o == "-q":
        file_of_queries = a
    elif o == "-o":
        file_of_output = a
    else:
        assert False, "unhandled option"

if (
    dictionary_file == None
    or postings_file == None
    or file_of_queries == None
    or file_of_output == None
):
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
