#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import glob
import pickle
import math

ps = nltk.stem.PorterStemmer()


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -i directory-of-documents -d dictionary-file -p postings-file"
    )


# Resets the disk folder. Wipes out the intermediate files
def reset_disk(out_dict, out_postings):
    dir_name = os.path.join(os.path.dirname(__file__), "disk")

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    for f in os.listdir(dir_name):
        file_path = os.path.join(dir_name, f)
        os.remove(file_path)

    out_dict_file = os.path.join(os.path.dirname(__file__), out_dict)
    out_postings_file = os.path.join(os.path.dirname(__file__), out_postings)

    # empty out the current dictionary.txt and postings.txt by opening in write mode
    with open(out_dict_file, "w") as f:
        pass

    with open(out_postings_file, "w") as f:
        pass


# Writes out the intermediate files to the 'disk'
def write_term_postings_dict_to_disk(term_postings_dict, block_num):
    # Get disk directory to write to
    dir_name = os.path.join(os.path.dirname(__file__), "disk")

    # Write full block from main memory to disk
    file_name = os.path.join(dir_name, "block_{}".format(block_num))
    with open(file_name, "wb") as outfile:  # Serialize block's dictionary to disk
        # Sort the postings lists according to the term lexicographically, and the postings list in numerical ascending order
        for term in sorted(term_postings_dict.keys()):
            postings_list = sorted(term_postings_dict[term])
            term_postings = [term, postings_list]
            pickle.dump(
                term_postings, outfile
            )  # Store each <term, postings list> to the disk block
        outfile.close()


# Helps to build up the intermediate files before merging. Returns number of intermediate blocks that have been generated
def build_intermediate_files(in_dir, BLOCK_SIZE):
    term_postings_dict = (
        {}
    )  # The current dictionary <term, [posting_list]> for each of the blocks
    block_num = (
        1  # Block number to write out intermediate blocks to disk (block file name)
    )
    size_used = 0  # Running counter to track how much memory we have used up

    # Read in documents to index
    doc_ids = os.listdir(in_dir)  # Read in paths of all documents in the in_dir
    doc_ids = [int(doc_id) for doc_id in doc_ids]
    doc_ids.sort()

    # save all the document IDs into its own file for NOT queries in search
    f_doc_ids = open(os.path.join(os.path.dirname(__file__), "doc_ids"), "wb")

    pickle.dump(doc_ids, f_doc_ids)

    # Process every document and create a dictionary of posting lists
    for docID in doc_ids:
        f = open(os.path.join(in_dir, str(docID)), "r")  # Open the document file
        text = f.read()  # Read the document in fulltext
        text = text.lower()  # Convert text to lower case
        sentences = nltk.sent_tokenize(text)  # Tokenize by sentence

        for sentence in sentences:
            words = nltk.word_tokenize(sentence)  # Tokenize by word
            words_stemmed = [ps.stem(w) for w in words]  # Stem every word

            for word in words_stemmed:
                # Before we add anything to the dictionary, we need to check that it will not exceed main memory
                # CASE 1: Check if word doesn't exist in dictionary
                if word not in term_postings_dict:
                    word_posting_size = sys.getsizeof(word) + sys.getsizeof(docID)

                    # Check that if we add this new term in, we won't exceed the block's memory size
                    # If exceed, we need to write block to disk (temporary postings file) and clear the memory
                    if word_posting_size + size_used > BLOCK_SIZE:
                        write_term_postings_dict_to_disk(
                            term_postings_dict, block_num
                        )  # Write block's dictionary to disk
                        block_num += (
                            1  # Increase block number that we have stored in disk
                        )
                        size_used = 0  # Reset size used in main memory
                        term_postings_dict.clear()  # Clear the in memory dictionary for the next block

                    # Add new term into block's dictionary
                    term_postings_dict[word] = [docID]
                    size_used += word_posting_size  # Increase size used in main memory

                # CASE 2: If word is inside dictionary
                else:
                    # If docID is not inside the postings list, need to check if we have memory to add to postings list
                    # If docID is already inside the postings list for this term, don't need to do anything
                    if docID not in term_postings_dict[word]:
                        # If exceed, we need to write block to disk (temporary postings file) and clear the memory
                        docID_size = sys.getsizeof(docID)

                        if docID_size + size_used > BLOCK_SIZE:
                            write_term_postings_dict_to_disk(
                                term_postings_dict, block_num
                            )  # Write block's dictionary to disk
                            block_num += (
                                1  # Increase block number that we have stored in disk
                            )
                            size_used = 0  # Reset size used in main memory
                            term_postings_dict.clear()  # Clear the in memory dictionary for the next block

                            # We need to add the the term to the cleared dictionary
                            term_postings_dict[word] = [docID]
                            size_used += (
                                sys.getsizeof(word) + docID_size
                            )  # Increase size of main memory used
                        else:
                            # The dictionary is still in main memory and we can just append the new docID to the postings list
                            term_postings_dict[word].append(docID)
                            size_used += docID_size  # Increase size of main memory used

        # Close the file
        f.close()

    # Write out the last block in main memory to the disk
    write_term_postings_dict_to_disk(
        term_postings_dict, block_num
    )  # Write block's dictionary to disk
    size_used = 0  # Reset size used in main memory
    term_postings_dict.clear()  # Clear the in memory dictionary for the next block

    return block_num


# Add in skip pointers for a posting_list
def add_skip_pointers(posting_list_to_merge):
    skip_pointer_number = int(math.sqrt(len(posting_list_to_merge)))
    skip_pointer_interval = len(posting_list_to_merge) // skip_pointer_number

    skip_pointer_marker = "^"
    current_skip_pointer_index = 0

    for i in range(skip_pointer_number):
        target_skip_index = 1 + current_skip_pointer_index + skip_pointer_interval

        # if the target_skip_index is going to be the very last element, or exceeds the last element of our list, just set it to point to the last
        if target_skip_index >= len(posting_list_to_merge):
            target_skip_index = len(posting_list_to_merge)

        # add in our skip pointers BEFORE the element that we are doing a comparison with
        posting_list_to_merge.insert(
            current_skip_pointer_index, "^" + str(target_skip_index)
        )
        current_skip_pointer_index = target_skip_index

    # example output with original posting_list_to_merge = [1,2,3,4,5,6,7,8,9]
    # skip pointers added --> [^4, 1,2,3,^8, 4,5,6,^11, 7,8,9]

    return posting_list_to_merge


# Used to build up the dictionary.txt and postings.txt
def write_to_disk(writeout_chunk, out_dict, out_postings):
    # open our dictionary and postings file
    # open does not mean load into memory

    f_dict = open(os.path.join(os.path.dirname(__file__), out_dict), "r+b")

    f_postings = open(os.path.join(os.path.dirname(__file__), out_postings), "r+b")

    # load in entire dictionary. this is ok, dictionary is relatively tiny compared to postings file

    dictionary = {}
    if os.stat(os.path.join(os.path.dirname(__file__), out_dict)).st_size != 0:
        dictionary = pickle.load(f_dict)

    # within writeout_chunk, every entity represents one dictionary + one posting_list entry
    for term_postings in writeout_chunk:
        f_postings.seek(0, 2)  # bring the pointer to the very end of the postings file
        pointer = (
            f_postings.tell()
        )  # get the byte offset of the final position, this will be where the posting_list is appended to

        # add in entry to our dictionary
        dictionary[term_postings["word"]] = {
            "doc_freq": term_postings["doc_freq"],
            "pointer": pointer,
        }

        # write the posting_list into into the postings.txt file at the very end
        # this directly writes into the file already
        pickle.dump(term_postings["posting_list"], f_postings)

    # rewrite the entire dictionary file with our new dictionary
    f_dict.seek(0, 0)  # bring pointer to the front
    f_dict.truncate()  # delete everything in the file from this point on
    pickle.dump(dictionary, f_dict)  # write the updated dictionary into dictionary.txt

    # close our files
    f_dict.close()
    f_postings.close()


# SPIMI algorithm
def spimi(CHUNK_SIZE, out_dict, out_postings):
    """==================================================================
    open up every file
    opening file DOES NOT loading file contents into memory
    =================================================================="""

    # Get disk directory to load in blocks
    disk_files = os.listdir(
        os.path.join(os.path.dirname(__file__), "disk")
    )  # Read in all documents in the disk

    # Process every file and deserialize them chunk by chunk
    open_disk_files = []

    """ ==================================================================
    we are doing n-way merging
    a chunk of data will be read off each intermediate file
    CHUNK_SIZE is smaller than BLOCK_SIZE by a factor of BLOCK_SIZE / (num_blocks + 1)
    this is to make space for a holding chunk called writeout_chunk that allows us to perform the merge
    ================================================================== """
    # Holding variable for the data head of every file to be merged
    chunks = [[] for i in range(len(disk_files))]

    for disk_file in disk_files:
        f = open(
            os.path.join(os.path.dirname(__file__), "disk", disk_file), "rb"
        )  # Open the block file

        # Maintain a reference to each opened block file so we can read chunks from all of them simultaneously
        open_disk_files.append(f)

    # Loads data from a block in disk into its designated chunk in main memory
    def load_chunk(block_ID):
        chunk_size_read = 0
        file_chunk = []  # This particular chunk of data from a block

        while chunk_size_read < CHUNK_SIZE:
            try:  # Read in line by line until chunk size in main memory is filled up
                deserialized_object = pickle.load(open_disk_files[block_ID])
                file_chunk.append(deserialized_object)
                chunk_size_read += sys.getsizeof(deserialized_object)
            except:
                break  # Nothing more to read

        chunks[block_ID] = file_chunk

        # If there is data in the chunk return true, else return false
        if len(file_chunk) > 0:
            return True
        else:
            return False

    # Load in initial chunk from each of the disk blocks
    for block_ID in range(len(open_disk_files)):
        load_chunk(block_ID)

    # This is the chunk that we will use as an in-memory holding variable
    # When full, will trigger the writing to dictionary.txt and postings.txt
    writeout_chunk = []
    writeout_memory_used = 0

    word_to_merge = ""
    chunk_ids_to_merge = []
    posting_list_to_merge = []
    doc_freq = 0

    """ ==================================================================
    merge code
    once the writeout_chunk is full, we will write it out to make space
    keep repeating until there are no more words to merge, then break out of while    
    ================================================================== """
    # Merge process across all the chunks. Load in more data from specific chunk if it runs out
    while True:
        """==================================================================
        we already know that all the blocks in disk have been lexicographically sorted
        this allows us to merge properly by simply considering the head of every chunk

        merge the heads where possible
        chunk format --- ['zero', ['14313', '14483', '1560', '1640']]
        =================================================================="""
        for chunkID, chunk in enumerate(chunks):
            # Load in data from chunk if it's empty and still has data
            if len(chunk) == 0:
                chunk_still_has_data = load_chunk(chunkID)  # Load in data into chunk
                if not chunk_still_has_data:  # If no more data just skip this chunk
                    continue

            # If we reach here, chunk has data and we need to merge and compare
            chunk = chunks[chunkID]
            if len(chunk) != 0:
                if word_to_merge == "":
                    word_to_merge = chunk[0][0]
                    chunk_ids_to_merge.append(chunkID)
                else:
                    if chunk[0][0] == word_to_merge:
                        chunk_ids_to_merge.append(chunkID)
                    elif chunk[0][0] < word_to_merge:
                        word_to_merge = chunk[0][0]
                        chunk_ids_to_merge.clear()
                        chunk_ids_to_merge.append(chunkID)

        # if we have no target word to merge, it means every chunk is empty and has no more data to be read
        # exit the while loop
        if word_to_merge == "":
            break

        for chunkID in chunk_ids_to_merge:
            # get the head and remove from the existing array
            posting_list_to_merge += chunks[chunkID].pop(0)[1]

        """ ==================================================================
        we know that disjointed posting lists are sorted, but may contain duplicates
        we need to remove duplicates and perform sorting on joined posting lists
        ================================================================== """
        # get the unique and sorted posting_list
        posting_list_to_merge = list(set(posting_list_to_merge))
        posting_list_to_merge.sort()
        doc_freq = len(posting_list_to_merge)

        # add in skip pointers to posting_list_to_merge
        posting_list_to_merge = add_skip_pointers(posting_list_to_merge)

        # calculate the new memory size needed for our new entry
        writeout_memory = (
            sys.getsizeof(len(posting_list_to_merge))
            + sys.getsizeof(word_to_merge)
            + sys.getsizeof(posting_list_to_merge[0]) * len(posting_list_to_merge)
        )

        """ ==================================================================
        write out to disk once writeout_chunk is full 
        once flushed to disk, continue
        ================================================================== """
        # if we exceed our CHUNK_SIZE, it is time to write out the terms merged thus far
        if writeout_memory + writeout_memory_used > CHUNK_SIZE:
            # write out to dictionary.txt and postings.txt
            write_to_disk(writeout_chunk, out_dict, out_postings)

            writeout_chunk.clear()
            writeout_memory_used = 0

        # either haven't exceed CHUNK_SIZE, or we have written out our current writeout_chunk
        writeout_chunk.append(
            {
                "word": word_to_merge,
                "doc_freq": doc_freq,
                "posting_list": posting_list_to_merge,
            }
        )
        writeout_memory_used += writeout_memory

        # clear out holding variables
        word_to_merge = ""
        chunk_ids_to_merge = []
        posting_list_to_merge = []
        doc_freq = 0

    print("Finished indexing")


# Main function
def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("indexing...\n")
    # This is an empty method
    # Pls implement your code in below

    # Define constants and variables (in bytes)
    reset_disk(out_dict, out_postings)  # Reset disk
    BLOCK_SIZE = 5000000  # Size of a block (main memory)

    # Calling build_intermediate_files(in_dir, BLOCK_SIZE) will create all the "blocks"
    BLOCKS_CREATED = build_intermediate_files(in_dir, BLOCK_SIZE)

    # Now we need to load each block chunk by chunk and do a single pass merge
    CHUNK_SIZE = BLOCK_SIZE // (
        BLOCKS_CREATED + 1
    )  # Get estimated chunk size to load in from each block

    # call our SPIMI function
    spimi(CHUNK_SIZE, out_dict, out_postings)


# Main

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
