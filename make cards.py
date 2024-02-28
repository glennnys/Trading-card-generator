import main
import os


inputs_path = "card files/"


# iterate through each text file in source files
filelist = os.listdir(inputs_path)
for i in filelist:
    if i.endswith(".txt"):
        with open(inputs_path + i, 'r') as f:
            main.generate_card_from_file(f)