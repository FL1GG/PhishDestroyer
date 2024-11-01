from names_dataset import NameDataset
import os
import random

nd = NameDataset() # 730k first names, 980k last names from https://github.com/philipperemy/name-dataset

first_names = list(nd.first_names.keys())
last_names = list(nd.last_names.keys())


class Profile:
    def __init__(self):
        self.firstname = self.getFirstName()
        self.lastname = self.getLastName()
        self.email = ""
        self.address = ""
        self.creditcard = ""


    def getFirstName(self):
        # since we are using a lot of data, best to use moreish random for each instance
        return random.SystemRandom().choice(first_names)

    def getLastName(self):
        return random.SystemRandom().choice(last_names)
    

    

x = Profile()
print(x.firstname)
print(x.lastname)
