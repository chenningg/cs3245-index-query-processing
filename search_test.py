import os
import nltk


# Set operator precedence to
def shunting_yard():
    operators = ["NOT", "AND", "OR", "ANDNOT"]
    operator_precedence = {"NOT": 2, "AND": 1, "ANDNOT": 1, "OR": 0}


queries = []
with open("queries.txt", "r") as input_file:
    for query in input_file.readlines():
        queries.append(query.rstrip())

print(queries)