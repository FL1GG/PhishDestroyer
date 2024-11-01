import os
import random
import string
import argparse
import requests
from random_user_agent.user_agent import UserAgent
import sys

# create a trueish random variable
r = random.SystemRandom()

# load everything into memory for increased speed
password_list = []
with open("configs/passwords.txt", "r", encoding='latin-1') as f:
    raw_dat = f.read() #this is really dependant that the file isn't larger than memory. #TODO improve this
    password_list = raw_dat.split('\n')

email_domains = []
with open("configs/email-domains.txt", "r") as f:
    raw_dat = f.read() #this is really dependant that the file isn't larger than memory. #TODO improve this
    email_domains = raw_dat.split('\n')

sites = []
with open("configs/sites.txt", "r") as f:
    raw_dat = f.read() #this is really dependant that the file isn't larger than memory. #TODO improve this
    sites = raw_dat.split('\n')

first_names = []
with open("configs/firstnames.txt", "r") as f:
    raw_dat = f.read() #this is really dependant that the file isn't larger than memory. #TODO improve this
    first_names = raw_dat.split('\n')

last_names = []
with open("configs/lastnames.txt", "r") as f:
    raw_dat = f.read() #this is really dependant that the file isn't larger than memory. #TODO improve this
    last_names = raw_dat.split('\n')


if(len(first_names) <= 1 or len(last_names) <= 1):
    from names_dataset import NameDataset
    nd = NameDataset() # 730k first names, 980k last names from https://github.com/philipperemy/name-dataset

if(len(first_names) <= 1):
    first_names = list(nd.first_names.keys())

if(len(last_names) <= 1):
    last_names = list(nd.last_names.keys())

class Profile:
    def __init__(self):
        self.firstname = self.getFirstName()
        self.lastname = self.getLastName()
        self.userName = self.getUserName()
        self.email = self.getEmail()
        self.password = self.getPassword()


        # TODO Future work
        self.address = "" #openaddress potentially
        self.creditcard = "" #https://github.com/wcDogg/python-cc-num-gen/tree/main


    def getFirstName(self):
        # since we are using a lot of data, best to use moreish random for each instance
        return r.choice(first_names)

    def getLastName(self):
        return r.choice(last_names)
    
    
    def getUserName(self):

        # create the first section of the email
        # TODO add more format options, phishers potentially filter out emails using name. May need random words.
        common_formats = ["{f}{last}", "{first}.{last}", "{first}_{last}", "{first}{last}", "{f}.{last}"] 

        format = r.choice(common_formats)

        username = ""

        match format:
            case "{f}{last}":
                username += self.firstname[0] + self.lastname
            case "{first}.{last}":
                username += self.firstname + "." + self.lastname
            case "{first}_{last}":
                username += self.firstname + "_" + self.lastname
            case "{first}{last}":
                username += self.firstname + self.lastname
            case "{f}.{last}":
                username += self.firstname[0] + "." + self.lastname


        # add a number in 30% of cases to increase variation
        if(r.random() < .3):
            username += str(r.randint(0, 100)) # adds 2 numbers, #TODO may want to make this a year later (4 nums)

        return username.replace(" ", "") # some names contain spaces

    def getEmail(self):
        ending = r.choice(email_domains)
        email = self.userName + "@" + ending

        return email
    

    def getPassword(self):
        return self.randomize_password(r.choice(password_list))
            

    # randomize the case of the password, #TODO substitution or endings such as @, !, etc..
    def randomize_password(self, password):
        new_pass = ""
        password = password.upper().lower()
        for i in password:
            if(r.random() > .5):
                new_pass += i.upper()
            else:
                new_pass += i

        return new_pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="PhishDestroyer",
        description="A program designed to ruin the databases of phishing attacks. It creates plausibly real people and injects them into a phishing site.")
    
    parser.add_argument('url', help="the url of the data to submit")
    parser.add_argument("-d", "--data", help="""the post data to be submitted. data should be submitted with 
                                                {f} meaning firstname
                                                {l} meaning lastname
                                                {u} meaning username
                                                {e} meaning email
                                                {p} meaning password
                                                """)
    
    # TODO, request type, headers, cookies, [look at sqlmap options]

    args = parser.parse_args()


    user_agent_rotator = UserAgent()
    
    while True:
        #construct a profile
        prof = Profile()

        #construct a request
        
        user_agent = user_agent_rotator.get_random_user_agent()

        headers = {
            "User-Agent": user_agent,
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Forwarded-For": str(r.randint(10,200)) + "." + str(r.randint(0,255))  + "." + str(r.randint(0,255)) + "." + str(r.randint(0,255)) # why not
        }

        raw_data = args.data.split("&")

        data = {}

        for rd in raw_data:
            rd = rd.replace("{f}", prof.firstname).replace("{l}", prof.lastname).replace("{u}", prof.userName).replace("{e}", prof.email).replace("{p}", prof.password)

            data[rd.split("=")[0]] = rd.split("=")[1]

        print(data)

        sess = requests.Session()

        sess.post(args.url, data=data, headers=headers, allow_redirects=False)


