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
        self.email = self.getEmail()
        self.password = self.getPassword()


        # Future work
        self.address = ""
        self.creditcard = ""


    def getFirstName(self):
        # since we are using a lot of data, best to use moreish random for each instance
        return random.SystemRandom().choice(first_names)

    def getLastName(self):
        return random.SystemRandom().choice(last_names)
    
    
    def getEmail(self):

        # create the first section of the email
        # TODO add more format options, phishers potentially filter out emails using name. May need random words.
        common_formats = ["{f}{last}", "{first}.{last}", "{first}_{last}", "{first}{last}", "{f}.{last}"] 

        format = random.SystemRandom().choice(common_formats)

        email = ""

        match format:
            case "{f}{last}":
                email += self.firstname[0] + self.lastname
            case "{first}.{last}":
                email += self.firstname + "." + self.lastname
            case "{first}_{last}":
                email += self.firstname + "_" + self.lastname
            case "{first}{last}":
                email += self.firstname + self.lastname
            case "{f}.{last}":
                email += self.firstname[0] + "." + self.lastname


        # add a number in 30% of cases to increase variation
        if(random.SystemRandom().random() < .3):
            email += str(random.SystemRandom().randint(0, 100)) # adds 2 numbers, #TODO may want to make this a year later (4 nums)


        #TODO add fuzzing for .gov, .mil type emails
        common_endings = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "zoho.com"]

        ending = random.SystemRandom().choice(common_endings)

        email += "@" + ending

        return email.replace(" ", "") # some names contain spaces
    

    def getPassword(self):
        pass
    
for x in range(10):
    x = Profile()
    print(x.firstname)
    print(x.lastname)
    print(x.email)
    print(x.address)
    print(x.creditcard)
    print("")
