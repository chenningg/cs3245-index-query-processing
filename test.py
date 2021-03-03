import pickle
import os



def write_to_disk():

    # writeout_chunk -> dictionary, posting_list

    # for posting_list in posting_lists:
    #     getfinalbyteoffsetofpostings.txttoappendtoendoffile
    #     --> add in pointer to dictionary
    #     add posting_list into the postings.txt
        

    # load in dictionary.txt
    # add in newwords to dictionary.txt 
    
    # {   
    #     "word": word_to_merge,
    #     "doc_freq" : doc_freq,
    #     "posting_list": posting_list_to_merge,
    #     "pointer": None
    # }


    # open our dictionary and postings file
    # open does not mean load into memory 
    f_dict = open(
        os.path.join(os.path.dirname(__file__), "dictionary.txt"), "rb"
    )
    
    dictionary = pickle.load(f_dict)
    print(len(dictionary.keys()))




    
    f_postings = open(
        os.path.join(os.path.dirname(__file__), "postings.txt"), "rb"
    )

    count = 0
    while True:
        try:
            postings = pickle.load(f_postings)
            count += 1
        except:
            break
    print(count)

    






        
    
    return

write_to_disk()