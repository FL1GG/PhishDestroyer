from names_dataset import NameDataset
import os
import random
import string
import argparse
import requests
from random_user_agent.user_agent import UserAgent


nd = NameDataset() # 730k first names, 980k last names from https://github.com/philipperemy/name-dataset

first_names = list(nd.first_names.keys())
last_names = list(nd.last_names.keys())

r = random.SystemRandom()

user_agent_rotator = UserAgent()

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
        #TODO add fuzzing for .gov, .mil type emails
        common_endings = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "zoho.com"]

        ending = r.choice(common_endings)

        email = self.userName + "@" + ending

        return email
    

    def getPassword(self):
        # three types of passwords currently, Rockyou, 4 word combinations, and true random passwords
        formats = ["rockyou", "4word", "random"]
        fmt = r.choice(formats)

        password = ""

        match fmt:
            case "rockyou":
                with open("data/10-million-password-list-top-1000000.txt", "r", encoding='latin-1') as f:
                    raw_dat = f.read()
                    org_pass = r.choice(raw_dat.split('\n'))

                    password = self.randomize_password(org_pass)
            case "4word":
                with open("data/words_alpha.txt", "r", encoding='latin-1') as f:
                    raw_dat = f.read()
                    words = raw_dat.split('\n')

                    org_pass = r.choice(words) + r.choice(words) + r.choice(words) + r.choice(words)

                    password = self.randomize_password(org_pass)

            case "random":
                characters = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(string.digits) + list(string.punctuation)
                for i in range(r.randint(6,17)):
                    password += r.choice(characters)
                

        return password


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


