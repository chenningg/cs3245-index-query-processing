#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle

ps = nltk.stem.PorterStemmer()

# Store valid operators as well as their precedence level (higher is more precendent)
OPERATORS = ["NOT", "AND", "OR"]
OPERATOR_PRECEDENCE = {"NOT": 2, "AND": 1, "OR": 0}


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
    )


# Parses a query into proper notation for shunting yard algorithm to process
def parse(query):
    if query == "":
        return []
    
    # Split by spaces in the query to extract terms
    # Tokens before processing, remove whitespace
    raw_tokens = query.rstrip().split(" ")
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
    # Define output queue and operator stack
    output_queue = []  # The reverse polish notation output
    operator_stack = []

    # Read in each token
    while tokens:
        token = tokens.pop(0)

        # If token is not an operator nor parenthesis, simply push it to the output queue
        if (token not in OPERATORS) and token != "(" and token != ")":
            # Make the token lower case and stem the token so that it will match the dictionary
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
                print("Mismatched parenthesis detected for query '{}'".format(query))
                return []  # Return empty list (error)

    # After while loop, if no more tokens to read, pop all remaining operators to output
    if not tokens:
        while operator_stack:
            # make sure that we do not care about malformed single left bracket queries
            operator = operator_stack.pop()

            if operator == "(":
                print("Mismatched parenthesis detected for query '{}'".format(query))
                return []
            output_queue.append(operator)

    return output_queue


# obtain the postings_list for a specific term from the f_postings file
# we are using seek, hence we only load the required portion
def get_postings_list(term, dictionary, f_postings):
    try:
        pointer = dictionary[term]["pointer"]  # get pointer value
        f_postings.seek(pointer, 0)  # bring the pointer to the postings_list of term_1
        # read out the associated posting list for the term
        postings_list = pickle.load(f_postings)
    except:
        postings_list = []
    return postings_list


# checks if an element in a postings_list is a skip pointer. skip pointers are strings, with a leading ^ symbol
def skip_pointer_check(value):
    # skip pointers are strings. convert to integer and return to be used as list index
    if isinstance(value, str):
        return int(value[1:])
    # if not skip pointer, we set to none
    else:
        return None


""" ==================================================================
handle NOT operator
incoming input: query_not(intermediate_results, all_doc_ids)
    intermediate_results --> postings_list_1
    all_doc_ids --> postings_list_2
we want the difference between them,
    postings_list_2 - postings_list_1
================================================================== """


def query_not(postings_list_1, postings_list_2):
    query_results = []  # holding list for valid doc_ids
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
            return query_results
        # if postings_list_1 is exhausted, the remainder of postings_list_2 will be added into results then returned
        elif curr_index_1 >= len(postings_list_1):
            for value in postings_list_2[curr_index_2:]:
                if skip_pointer_check(value) == None:
                    query_results.append(value)
            return query_results

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

        """ ==================================================================
        1==2 : equality comparison
        since we want the difference, we do not want values of equality 
        ================================================================== """
        if curr_value_1 == curr_value_2:
            # move up both indexes and do not add anything to results. cannot skip here!
            curr_index_1 += 1
            curr_index_2 += 1

            """ ==================================================================
            2 < 1 : smaller comparison 
            we want the values of this if true
            using the process of 
                curr_value_2 < curr_value_1 --> append and advance curr_value_2
            ================================================================== """
        elif curr_value_2 < curr_value_1:
            query_results.append(curr_value_2)

            # advance curr_index_2 --> check skip pointer first

            # if skip_pointer exists, we check the value to the pointers' right (skip pointers point to other skip pointers)
            if skip_pointer_2 != None:
                # The last skip pointer points to last element in the postings list
                if skip_pointer_2 == len(postings_list_2) - 1:
                    skip_value_2 = postings_list_2[skip_pointer_2]
                # Otherwise, get the value of the posting that the skip pointer points to
                else:
                    skip_value_2 = postings_list_2[skip_pointer_2 + 1]

                # if the value that the skip_pointer points towards is something still smaller then all intermediate results are safe
                if skip_value_2 <= curr_value_1:
                    # append all values prior to the results
                    for doc_id in postings_list_2[curr_index_2 + 1 : skip_pointer_2]:
                        query_results.append(doc_id)

                    # if we skipped ahead, we need to update our pointers
                    curr_index_2 = skip_pointer_2 + 1
                    skip_pointer_2 = skip_pointer_check(postings_list_2[skip_pointer_2])
                else:
                    # failed to skip, continue linearly
                    curr_index_2 += 1
            else:
                # skip pointer invalid, just increment by 1
                curr_index_2 += 1

            """ ==================================================================
            2 > 1 : greater comparison 
            we do not want this
            
            advance the pointer without appending 
            ================================================================== """
        elif curr_value_2 > curr_value_1:
            # advance curr_index_1 --> check skip pointer first

            # if skip_pointer exists, we check the value to the pointers' right (skip pointers point to other skip pointers)
            if skip_pointer_1 != None:
                # The last skip pointer points to last element in the postings list
                if skip_pointer_1 == len(postings_list_1) - 1:
                    skip_value_1 = postings_list_1[skip_pointer_1]
                # Otherwise, get the value of the posting that the skip pointer points to
                else:
                    skip_value_1 = postings_list_1[skip_pointer_1 + 1]

                # if the value that the skip_pointer points towards is something still smaller then all intermediate results are safe
                if skip_value_1 <= curr_value_2:

                    # if we skipped ahead, we need to update our pointers
                    curr_index_1 = skip_pointer_1 + 1
                    skip_pointer_1 = skip_pointer_check(postings_list_1[skip_pointer_1])
                else:
                    # failed to skip, continue linearly
                    curr_index_1 += 1
            else:
                # skip pointer invalid, just increment by 1
                curr_index_1 += 1

    return query_results


""" ==================================================================
handle AND operator
incoming input: query_and(intermediate_results, postings_list_term_2)
    intermediate_results --> postings_list_1
    postings_list_term_2 --> postings_list_2
we want the intersection between them,
    intersection(posting_list_1, posting_list_2)
================================================================== """


def query_and(postings_list_1, postings_list_2):
    query_results = []  # holding list for valid doc_ids
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
            return query_results
        # as long as postings_list_1 is exhausted, we do not want the rest of postings_list_2
        elif curr_index_1 >= len(postings_list_1):
            return query_results

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

        """ ==================================================================
        1==2 : equality comparison
        since we want the intersection, we require values of equality
        ================================================================== """
        if curr_value_1 == curr_value_2:
            # move up both indexes and add one copy to results. cannot skip here!
            query_results.append(curr_value_1)

            curr_index_1 += 1
            curr_index_2 += 1

            """ ==================================================================
            2 < 1 : smaller comparison 
            we do not want this if true
            
            advance the pointer without appending 
            ================================================================== """
        elif curr_value_2 < curr_value_1:
            # advance curr_index_2 --> check skip pointer first

            # if skip_pointer exists, we check the value to the pointers' right (skip pointers point to other skip pointers)
            if skip_pointer_2 != None:
                # The last skip pointer points to last element in the postings list
                if skip_pointer_2 == len(postings_list_2) - 1:
                    skip_value_2 = postings_list_2[skip_pointer_2]
                # Otherwise, get the value of the posting that the skip pointer points to
                else:
                    skip_value_2 = postings_list_2[skip_pointer_2 + 1]

                # if the value that the skip_pointer points towards is something still smaller then all intermediate results are safe
                if skip_value_2 <= curr_value_1:
                    # if we skipped ahead, we need to update our pointers
                    curr_index_2 = skip_pointer_2 + 1
                    skip_pointer_2 = skip_pointer_check(postings_list_2[skip_pointer_2])
                else:
                    # failed to skip, continue linearly
                    curr_index_2 += 1
            else:
                # skip pointer invalid, just increment by 1
                curr_index_2 += 1

            """ ==================================================================
            2 > 1 : greater comparison 
            we do not want this
            
            advance the pointer without appending 
            ================================================================== """
        elif curr_value_2 > curr_value_1:
            # advance curr_index_1 --> check skip pointer first

            # if skip_pointer exists, we check the value to the pointers' right (skip pointers point to other skip pointers)
            if skip_pointer_1 != None:
                # The last skip pointer points to last element in the postings list
                if skip_pointer_1 == len(postings_list_1) - 1:
                    skip_value_1 = postings_list_1[skip_pointer_1]
                # Otherwise, get the value of the posting that the skip pointer points to
                else:
                    skip_value_1 = postings_list_1[skip_pointer_1 + 1]

                # if the value that the skip_pointer points towards is something still smaller then all intermediate results are safe
                if skip_value_1 <= curr_value_2:

                    # if we skipped ahead, we need to update our pointers
                    curr_index_1 = skip_pointer_1 + 1
                    skip_pointer_1 = skip_pointer_check(postings_list_1[skip_pointer_1])
                else:
                    # failed to skip, continue linearly
                    curr_index_1 += 1
            else:
                # skip pointer invalid, just increment by 1
                curr_index_1 += 1

    return query_results


""" ==================================================================
handle OR operator
incoming input: query_or(intermediate_results, postings_list_term_2)
    intermediate_results --> postings_list_1
    postings_list_term_2 --> postings_list_2
we want the union between them,
    union(posting_list_1, posting_list_2)
================================================================== """


def query_or(postings_list_1, postings_list_2):
    query_results = []  # holding list for valid doc_ids
    skip_marker = "^"  # the indicator of a skip pointer

    # the index we are on for the respective lists right now
    curr_index_1 = curr_index_2 = 0

    # which index should we be skipping to next, if possible
    skip_pointer_1 = skip_pointer_2 = 0

    # while loop ends when we reach the end of both posting lists
    while True:
        # terminating conditions
        # if postings_list_2 is exhausted, the remainder of postings_list_1 will be added into results then returned
        if curr_index_2 >= len(postings_list_2):
            for value in postings_list_1[curr_index_1:]:
                if skip_pointer_check(value) == None:
                    query_results.append(value)
            return query_results
        # if postings_list_1 is exhausted, the remainder of postings_list_2 will be added into results then returned
        elif curr_index_1 >= len(postings_list_1):
            for value in postings_list_2[curr_index_2:]:
                if skip_pointer_check(value) == None:
                    query_results.append(value)
            return query_results

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

        """ ==================================================================
        1==2 : equality comparison
        since we want the union, we will keep one copy for values of equality 
        ================================================================== """
        if curr_value_1 == curr_value_2:
            # move up both indexes and add one copy to results. cannot skip here!
            query_results.append(curr_value_1)

            curr_index_1 += 1
            curr_index_2 += 1

            """ ==================================================================
            2 < 1 : smaller comparison 
            we want the values of this if true
            using the process of 
                curr_value_2 < curr_value_1 --> append and advance curr_value_2
            ================================================================== """
        elif curr_value_2 < curr_value_1:
            query_results.append(curr_value_2)

            # advance curr_index_2 --> check skip pointer first

            # if skip_pointer exists, we check the value to the pointers' right (skip pointers point to other skip pointers)
            if skip_pointer_2 != None:
                # The last skip pointer points to last element in the postings list
                if skip_pointer_2 == len(postings_list_2) - 1:
                    skip_value_2 = postings_list_2[skip_pointer_2]
                # Otherwise, get the value of the posting that the skip pointer points to
                else:
                    skip_value_2 = postings_list_2[skip_pointer_2 + 1]

                # if the value that the skip_pointer points towards is something still smaller then all intermediate results are safe
                if skip_value_2 <= curr_value_1:
                    # append all values prior to the results
                    for doc_id in postings_list_2[curr_index_2 + 1 : skip_pointer_2]:
                        query_results.append(doc_id)

                    # if we skipped ahead, we need to update our pointers
                    curr_index_2 = skip_pointer_2 + 1
                    skip_pointer_2 = skip_pointer_check(postings_list_2[skip_pointer_2])
                else:
                    # failed to skip, continue linearly
                    curr_index_2 += 1
            else:
                # skip pointer invalid, just increment by 1
                curr_index_2 += 1

            """ ==================================================================
            2 > 1 : larger comparison 
            we want the values of this if true
            using the process of 
                curr_value_2 > curr_value_1 --> append and advance curr_value_1
            ================================================================== """
        elif curr_value_2 > curr_value_1:
            query_results.append(curr_value_1)

            # advance curr_index_1 --> check skip pointer first

            # if skip_pointer exists, we check the value to the pointers' right (skip pointers point to other skip pointers)
            if skip_pointer_1 != None:
                # The last skip pointer points to last element in the postings list
                if skip_pointer_1 == len(postings_list_1) - 1:
                    skip_value_1 = postings_list_1[skip_pointer_1]
                # Otherwise, get the value of the posting that the skip pointer points to
                else:
                    skip_value_1 = postings_list_1[skip_pointer_1 + 1]

                # if the value that the skip_pointer points towards is something still smaller then all intermediate results are safe
                if skip_value_1 <= curr_value_2:
                    # append all values prior to the results
                    for doc_id in postings_list_1[curr_index_1 + 1 : skip_pointer_1]:
                        query_results.append(doc_id)

                    # if we skipped ahead, we need to update our pointers
                    curr_index_1 = skip_pointer_1 + 1
                    skip_pointer_1 = skip_pointer_check(postings_list_1[skip_pointer_1])
                else:
                    # failed to skip, continue linearly
                    curr_index_1 += 1
            else:
                # skip pointer invalid, just increment by 1
                curr_index_1 += 1

    return query_results



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

        # empty query
        if parsed_query == []:
            results.append([])
            continue

        # print(query, ":", parsed_query)

        # holding variable for our stack of terms as we go through them one by one
        # this stack will also hold the results of our operations
        term_stack = []

        for token in parsed_query:
            # add into our term_stack
            if token not in OPERATORS:
                term_stack.append(token)
            # detect an operator
            else:
                # unary operator, applies to one term only
                if token == "NOT":
                    # get last term in term stack
                    term_1 = term_stack.pop()

                    # if the last term is not a list (aka result of previous operators), need to get posting list for this term
                    if not isinstance(term_1, list):
                        term_1 = get_postings_list(term_1, dictionary, f_postings)

                    # handle the not query against all doc ids
                    term_stack.append(query_not(term_1, all_doc_ids))

                # binary operators, applies to two terms
                else:
                    # pop last two terms in term_stack for binary operators
                    term_1 = term_stack.pop()
                    term_2 = term_stack.pop()

                    # if either is not a list (aka result from previous operation), get posting list of term
                    if not isinstance(term_1, list):
                        term_1 = get_postings_list(term_1, dictionary, f_postings)

                    if not isinstance(term_2, list):
                        term_2 = get_postings_list(term_2, dictionary, f_postings)

                    # do the respective operations on the last two terms in the term stack
                    if token == "AND":
                        term_stack.append(query_and(term_1, term_2))
                    elif token == "OR":
                        term_stack.append(query_or(term_1, term_2))
                    elif token == "ANDNOT":
                        term_stack.append(query_andnot(term_1, term_2))

        # if the query was just a single term without any operators just give back the posting list as the results
        if len(term_stack) > 1:
            print(
                "ERROR - phrasal queries not supported. Please do not give multiple isolated words without operators separating them"
            )
            term_stack = ["Error"]
        else:
            # get last result from term stack
            term_1 = term_stack.pop()

            # if the only term is not a list, means we had a term without operators, get its posting list
            if not isinstance(term_1, list):
                term_1 = get_postings_list(term_1, dictionary, f_postings)

            # spread all the values of the term nd remove all skip pointers
            for value in term_1:
                if not isinstance(value, str):
                    term_stack.append(value)

        # output to final results container
        results.append(term_stack)

    """ ==================================================================
    save out to results.txt
    just overwrite the entire file 
    ================================================================== """
    f_results = open(os.path.join(os.path.dirname(__file__), results_file), "w")

    for i, result in enumerate(results):
        if len(result) == 0:
            f_results.write("\n")
        else:
            result_string = " ".join([str(doc_id) for doc_id in result])
            result_string = result_string.rstrip()
            # result_string = "queries " + str(i) + " : " + result_string
            f_results.write(result_string + "\n")

    """ ==================================================================
    close out all files
    ================================================================== """
    f_dict.close()
    f_queries.close()
    f_postings.close()
    f_results.close()

    # """ ==================================================================
    # check output file
    # ================================================================== """
    # f_results = open(os.path.join(os.path.dirname(__file__), results_file), "r")

    # results = [result for result in f_results.read().splitlines()]
    # results = [result.split() for result in results]

    # for result in results:
    #     print(len(result))
    #     print(result)

    print(f"Finished search, please check output file {results_file}")


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
