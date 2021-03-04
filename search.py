#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle

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
    # Store valid operators as well as their precedence level (higher is more precendent)
    operators = ["NOT", "AND", "OR", "ANDNOT"]
    operator_precedence = {"NOT": 2, "AND": 1, "ANDNOT": 1, "OR": 0}
    operator_association = {
        "NOT": "RIGHT",
        "AND": "LEFT",
        "ANDNOT": "LEFT",
        "OR": "LEFT",
    }

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
        if (token not in operators) and token != "(" and token != ")":
            output_queue.append(token)
        # If token is an operator, need to check before pushing to operator stack
        elif token in operators:
            # Check if operator stack is not empty and current operator is smaller in precedence or is right associative
            # If so, push it to the operator stack (because it has smaller precedence). Otherwise, push all operators with precedence smaller than it to the output first.
            while (
                operator_stack
                and operator_stack[-1] != "("
                and (
                    operator_precedence[operator_stack[-1]] > operator_precedence[token]
                    or (
                        operator_precedence[operator_stack[-1]]
                        == operator_precedence[token]
                        and operator_association[token] == "LEFT"
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
            output_queue.append(operator_stack.pop())

    return output_queue


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"
    )


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
    ================================================================== """
    f_dict = open(os.path.join(os.path.dirname(__file__), dict_file), "rb")

    dictionary = pickle.load(f_dict)

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

        # holding variable for the posting lists that we will get
        posting_lists = []

        # query against the dictionary + posting list to get the necessary posting list

        # perform the required intersection/merge on posting_lists

    """ ==================================================================
    save out to results.txt
    just overwrite the entire file 
    ================================================================== """
    f_results = open(os.path.join(os.path.dirname(__file__), results_file), "w")

    results = [[12, 40, 45], [], [123, 456]]

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
