import pickle
import os
import nltk

ps = nltk.stem.PorterStemmer()


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
    all_doc_len = 7769

    for word in ["then", "there"]:
        try:
            print(dictionary[ps.stem(word)]["doc_freq"])
        except:
            print(0)

    
    doc_ids_file = "doc_ids"
    f_doc_ids = open(os.path.join(os.path.dirname(__file__), doc_ids_file), "rb")
    all_doc_ids = pickle.load(f_doc_ids)
    
    a = ['^4', 1680, 3563, 5109, '^8', 7539, 7907, 7934, '^11', 9293, 10005, 11222]
    b = ['^19', 5, 45, 110, 180, 203, 209, 748, 833, 857, 903, 926, 942, 969, 1088, 1110, 1207, 1387, 1414, '^38', 1477, 1499, 1616, 1657, 1682, 1711, 1731, 1777, 1836, 1839, 1848, 1858, 1863, 1880, 1889, 1909, 1926, 2064, '^57', 2087, 2190, 2269, 2286, 2354, 2376, 2383, 2467, 2475, 2521, 2554, 2747, 2775, 2799, 2833, 2896, 2924, 2925, '^76', 2955, 2959, 2979, 3023, 3024, 3056, 3094, 3117, 3155, 3198, 3261, 3512, 3532, 3534, 3535, 3571, 3593, 3699, '^95', 3795, 3864, 3931, 3982, 4005, 4026, 4031, 4052, 4063, 4093, 4127, 4133, 4174, 4233, 4290, 4369, 4382, 4392, '^114', 4440, 4477, 4490, 4518, 4548, 4549, 4593, 4625, 4662, 4689, 4713, 4903, 5109, 5139, 5160, 5162, 5167, 5171, '^133', 5176, 5193, 5194, 5273, 5288, 5290, 5318, 5345, 5363, 5376, 5408, 5467, 5511, 5561, 5598, 5690, 5761, 5808, '^152', 5850, 5888, 5954, 5985, 6079, 6091, 6127, 6157, 6296, 6337, 6338, 6350, 6373, 6400, 6471, 6493, 6531, 6578, '^171', 6606, 6665, 6708, 6719, 6720, 6746, 6770, 6815, 6869, 6876, 6922, 6945, 6954, 7109, 7150, 7326, 7366, 7375, '^190', 7391, 7429, 7443, 7499, 7552, 7576, 7659, 7662, 7669, 7710, 7765, 7918, 8008, 8009, 8044, 8088, 8097, 8102, '^209', 8106, 8113, 8135, 8156, 8186, 8189, 8240, 8427, 8441, 8535, 8554, 8563, 8578, 8596, 8598, 8608, 8676, 8681, '^228', 8765, 8922, 8943, 8944, 9015, 9022, 9055, 9069, 9110, 9138, 9216, 9283, 9382, 9415, 9470, 9532, 9535, 9554, '^247', 9603, 9604, 9617, 9654, 9689, 9697, 9795, 9797, 9804, 9816, 9923, 9957, 9975, 9978, 10005, 10049, 10078, 10080, '^266', 10091, 10106, 10124, 10168, 10228, 10230, 10306, 10344, 10347, 10382, 10537, 10539, 10548, 10569, 10617, 10665, 10689, 10695, '^285', 10696, 10760, 10768, 10771, 10780, 10781, 10807, 10872, 10902, 10905, 10931, 10944, 11000, 11007, 11074, 11076, 11118, 11123, '^304', 11222, 11254, 11287, 11390, 11397, 11430, 11437, 11487, 11504, 11506, 11541, 11555, 11599, 11637, 11658, 11734, 11739, 11830, '^323', 11858, 11861, 11882, 12027, 12136, 12145, 12197, 12203, 12208, 12213, 12261, 12333, 12447, 12472, 12827, 13046, 13144, 13649, 13856, 13904, 13950, 14199, 14270, 14739]

    c = []
    d = []
    for val in a:
        if isinstance(val, int):
            c.append(val)
    for val in b:
        if isinstance(val, int):
            d.append(val)     

    # f = []
    # g = []
    # for doc_id in all_doc_ids: 
    #     if doc_id not in c:
    #         f.append(doc_id)
    #     if doc_id not in d:
    #         g.append(doc_id)
    # print(len(set.intersection(set(f), set(g))))

    print(set.intersection(set(c), set(d)))



    
    # f_postings = open(
    #     os.path.join(os.path.dirname(__file__), "postings.txt"), "rb"
    # )

    # count = 0
    # while True:
    #     try:
    #         postings = pickle.load(f_postings)
    #         if count == 3:
    #         # if count == 2:
    #             print(postings)
    #         count += 1
    #     except:
    #         break
    # print(count)

    # print(isinstance('^18', str))

    






        
    
    return

write_to_disk()