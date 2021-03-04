This is the README file for A0228402N and A0230521Y's submission

== Python Version ==

We're using Python Version 3.8.5 for this assignment. We are operating on a Windows 10 environment
Standard python packages were used
	re	for regular expression
	nltk	for NLP
	sys	for system functions
	getopt	to get options in CLI
	os	to traverse os
	pickle 	to serialize objects in file saving
	glob	to list out filenames in directory
	math	for square root function

== General Notes about this assignment ==

Running index.py
Please provide the path to the reuters data in the command prompt
>>>	python index.py -i <path_to_reuters_data_here> -d dictionary.txt -p postings.txt

Running search.py
Please provide the target input file for the queries, and the target output file for the output
>>>	python search.py -d dictionary.txt -p postings.txt -q queries.txt -o outputs.txt 

We have heavily documented our code. Please refer to our code for explanation on what we have done
However as a summary, we have performed the following tasks
	1. Simulated memory limitations for blocks and chunks 
	2. creating an index using SPIMI 
	3. performed multi-way merge to create index
	4. implemented skip pointers within posting list
	5. allowed for posting lists to be loaded using pointers towards the postings.txt file
	6. parsed boolean retrieval queries through adapting Shunting-Yard algorithm and Reverse Polish Notation
	7. implemented boolean query operations through our own merge algorithm (no use of built-in functions)
	8. incorporated skip pointers within our merge algorithm
	9. retrieving answers for boolean queries

== Files included with this submission ==

index.py		implementation of index construction through SPIMI
search.py		implementation of the boolean retrieval function 
dictionary.txt		the corpus, obtained from parsing reuters data
postings.txt		the postings file, pointed to by dictionary entries
README.txt		this file you are reading

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0228402N and A0230521Y, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] We, A0228402N and A0230521Y did not follow the class rules regarding homework
assignment, because of the following reason:

We suggest that we should be graded as follows:

Normal

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

Tokenizing - https://pythonspot.com/tokenizing-words-and-sentences-with-nltk/
Stemming - https://www.geeksforgeeks.org/python-stemming-words-with-nltk/
Shunting yard algorithm - https://en.wikipedia.org/wiki/Shunting-yard_algorithm
Reverse polish notation - https://en.wikipedia.org/wiki/Reverse_Polish_notation
Parsing reverse polish notation - https://rosettacode.org/wiki/Parsing/RPN_calculator_algorithm#Python
CS3245 lecture notes
NTU CZ4031 notes for block-based approach to file IO

