import os
import pickle

disk_files = os.listdir(
    os.path.join(os.path.dirname(__file__), "disk")
)  # Read in all documents in the disk

# Process every file and deserialize them to view in txt format
for disk_file in disk_files[2:3]:
    f = open(
        os.path.join(os.path.dirname(__file__), "disk", disk_file), "rb"
    )  # Open the document file

    print("================{}=================".format(disk_file))

    while True:
        try:
            deserialized_file = pickle.load(f)
            print(deserialized_file)
        except:
            break
    f.close()
