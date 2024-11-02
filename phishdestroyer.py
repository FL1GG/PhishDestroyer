import random
import argparse
import requests
from random_user_agent.user_agent import UserAgent
import inspect
import sys

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

header = r"""
   ___  __   _     __   ___         __                       
  / _ \/ /  (_)__ / /  / _ \___ ___/ /________  __ _____ ____
 / ___/ _ \/ (_-</ _ \/ // / -_|_-< __/ __/ _ \/ // / -_) __/
/_/  /_//_/_/___/_//_/____/\__/___|__/_/  \___/\_, /\__/_/   
                                              /___/          
"""
print(header)

# create a trueish random
r = random.SystemRandom()

printProgressBar(1, 100, prefix = 'Progress:', suffix = 'Complete, Loading Passwords', length = 50)

# load everything into memory for increased speed
password_list = []
with open("configs/passwords.txt", "r", encoding='latin-1') as f:
    raw_dat = f.read() #this is really dependant that the file isn't larger than memory. #TODO improve this
    password_list = raw_dat.split('\n')

printProgressBar(1, 100, prefix = 'Progress:', suffix = 'Complete, Loading Email Domains', length = 50)


email_domains = []
with open("configs/email-domains.txt", "r") as f:
    raw_dat = f.read() #this is really dependant that the file isn't larger than memory. #TODO improve this
    email_domains = raw_dat.split('\n')

printProgressBar(20, 100, prefix = 'Progress:', suffix = 'Complete, Loading Sites', length = 50)

sites = []
with open("configs/sites.txt", "r") as f:
    raw_dat = f.read() #this is really dependant that the file isn't larger than memory. #TODO improve this
    sites = raw_dat.split('\n')

printProgressBar(30, 100, prefix = 'Progress:', suffix = 'Complete, Loading Username Rules', length = 50)

username_rules = []
with open("configs/username-rules.txt", "r") as f:
    for line in f:
        if(len(line.strip()) <= 0 or line.startswith("#")):
            continue

        username_rules.append(line.strip())

printProgressBar(40, 100, prefix = 'Progress:', suffix = 'Complete, Loading Password Rules', length = 50)


password_rules = []
with open("configs/password-rules.txt", "r") as f:
    for line in f:
        if(len(line.strip()) <= 0 or line.startswith("#")):
            continue

        password_rules.append(line.strip())

#stolen from https://github.com/iphelix/pack/blob/master/rulegen.py
# added bounds checking, some of these are getting incomprehensible
hashcat_rule = dict()

hashcat_rule[':'] = lambda x: x                                    # Do nothing

# Case rules
hashcat_rule["l"] = lambda x: x.lower()                            # Lowercase all letters
hashcat_rule["u"] = lambda x: x.upper()                            # Capitalize all letters
hashcat_rule["c"] = lambda x: x.capitalize()                       # Capitalize the first letter
hashcat_rule["C"] = lambda x: x[0].lower() + x[1:].upper()         # Lowercase the first found character, uppercase the rest
hashcat_rule["t"] = lambda x: x.swapcase()                         # Toggle the case of all characters in word
hashcat_rule["T"] = lambda x,y: x if int(y) >= len(x) else x[:int(y)] + x[int(y)].swapcase() + x[int(y)+1:]  # Toggle the case of characters at position N
hashcat_rule["E"] = lambda x: " ".join([i[0].upper()+i[1:] for i in x.split(" ")]) # Upper case the first letter and every letter after a space

# Rotation rules
hashcat_rule["r"] = lambda x: x[::-1]                              # Reverse the entire word
hashcat_rule["{"] = lambda x: x[1:]+x[0]                           # Rotate the word left
hashcat_rule["}"] = lambda x: x[-1]+x[:-1]                         # Rotate the word right

# Duplication rules
hashcat_rule["d"] = lambda x: x+x                                  # Duplicate entire word
hashcat_rule["p"] = lambda x,y: x*int(y)                                # Duplicate entire word N times
hashcat_rule["f"] = lambda x: x+x[::-1]                            # Duplicate word reversed
hashcat_rule["z"] = lambda x,y: x[0]*int(y)+x                           # Duplicate first character N times
hashcat_rule["Z"] = lambda x,y: x+x[-1]*int(y)                          # Duplicate last character N times
hashcat_rule["q"] = lambda x: "".join([i+i for i in x])            # Duplicate every character
hashcat_rule["y"] = lambda x,y: x[:int(y)]+x                            # Duplicate first N characters
hashcat_rule["Y"] = lambda x,y: x+x[-int(y):]                           # Duplicate last N characters

# Cutting rules
hashcat_rule["O"] = lambda x,y,z: x if int(y) >= len(x) else x[:int(y)] + x[int(z)-1:]                 #  Delete M characters, starting at position N 
hashcat_rule["["] = lambda x: x[1:]                                # Delete first character
hashcat_rule["]"] = lambda x: x[:-1]                               # Delete last character
hashcat_rule["D"] = lambda x,y: x if int(y) >= len(x) else x[:int(y)]+x[int(y)+1:]                      # Deletes character at position N
hashcat_rule["'"] = lambda x,y: x if int(y) >= len(x) else x[:int(y)]                              # Truncate word at position N
hashcat_rule["x"] = lambda x,y,z: x if int(y) >= len(x) or int(y)+int(z) > len(x) else x[:int(y)]+x[int(y)+z:]                    # Delete M characters, starting at position N #TODO bounds may chance how this rule works
hashcat_rule["@"] = lambda x,y: x.replace(y,'')                    # Purge all instances of X

# Insertion rules
hashcat_rule["$"] = lambda x,y: x+y                                # Append character to end
hashcat_rule["^"] = lambda x,y: y+x                                # Prepend character to front
hashcat_rule["i"] = lambda x,y,z: x if int(y) >= len(x) else x[:int(y)]+z+x[int(y):]                    # Insert character X at position N

# Replacement rules
hashcat_rule["o"] = lambda x,y,z: x if int(y) >= len(x) else x[:int(y)]+z+x[int(y)+1:]                  # Overwrite character at position N with X
hashcat_rule["s"] = lambda x,y,z: x.replace(y,z)                   # Replace all instances of X with Y
hashcat_rule["L"] = lambda x,y: x if int(y) >= len(x) else x[:int(y)]+chr(ord(x[int(y)])<<1)+x[int(y)+1:]    # Bitwise shift left character @ N
hashcat_rule["R"] = lambda x,y: x if int(y) >= len(x) else x[:int(y)]+chr(ord(x[int(y)])>>1)+x[int(y)+1:]    # Bitwise shift right character @ N
hashcat_rule["+"] = lambda x,y: x if int(y) >= len(x) else x[:int(y)]+chr(ord(x[int(y)])+1)+x[int(y)+1:]     # Increment character @ N by 1 ascii value
hashcat_rule["-"] = lambda x,y: x if int(y) >= len(x) else x[:int(y)]+chr(ord(x[int(y)])-1)+x[int(y)+1:]     # Decrement character @ N by 1 ascii value
hashcat_rule["."] = lambda x,y: x if int(y) >= len(x) else x[:int(y)]+x[int(y)+1]+x[int(y)+1:]               # Replace character @ N with value at @ N plus 1
hashcat_rule[","] = lambda x,y: x if int(y) >= len(x) else x[:int(y)]+x[int(y)-1]+x[int(y)+1:]               # Replace character @ N with value at @ N minus 1

# Swappping rules
hashcat_rule["k"] = lambda x: x[1]+x[0]+x[2:]                      # Swap first two characters
hashcat_rule["K"] = lambda x: x[:-2]+x[-1]+x[-2]                   # Swap last two characters
hashcat_rule["*"] = lambda x,y,z: x if int(z) >= len(x) or int(y) >= len(x) else (x[:int(y)]+x[int(z)]+x[int(y)+1:int(z)]+x[int(y)]+x[int(z)+1:] if int(z) > int(y) else x[:int(z)]+x[int(y)]+x[int(z)+1:int(y)]+x[int(z)]+x[int(y)+1:]) # Swap character X with Y

printProgressBar(50, 100, prefix = 'Progress:', suffix = 'Complete, Loading First and Last Names', length = 50)

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

printProgressBar(100, 100, prefix = 'Progress:', suffix = 'Complete'.ljust(40), length = 50)

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
        format = r.choice(username_rules)

        n2 = str(r.randint(0, 100))    

        username = format.replace("{f}", self.firstname[0]
                                ).replace("{first}", self.firstname
                                ).replace("{l}", self.lastname[0]
                                ).replace("{last}", self.lastname
                                ).replace("{n2}", n2)

        return username.replace(" ", "") # some names contain spaces

    def getEmail(self):
        ending = r.choice(email_domains)
        email = self.userName + "@" + ending

        return email
    

    def getPassword(self):
        return self.apply_password_rule(r.choice(password_list))
            

    # apply password rules from hashcat
    def apply_password_rule(self, password):
        rules = r.choice(password_rules)
        rules = ''.join(rules.split())

        index = 0
        while index < len(rules):
            rule = rules[index]
            #get number of parameters
            params = len(inspect.signature(hashcat_rule[rule]).parameters)

            if(params == 1):
                password = hashcat_rule[rule](password)
            elif(params == 2):
                password = hashcat_rule[rule](password, rules[index+1])
                index += 1
            elif(params == 3):
                password = hashcat_rule[rule](password, rules[index+1], rules[index+2])
                index += 2

            index += 1
            
        return password


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
        try:
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

            print(f'\r' + str(data), end='\r')

            sess = requests.Session()

            sess.post(args.url, data=data, headers=headers, allow_redirects=False)
        except KeyboardInterrupt as kb:
            print("")
            print("Gracefully exiting...")
            sys.exit()
        except Exception as e:
            print(e)



