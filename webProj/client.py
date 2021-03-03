#-----------------------------------------------------------------------------
# University of Leeds, School of Computing
# Client application to be used in Coursework 1 of COMP3011 2020-2021
# Written by Najmuddin Dost, 2019
# Najmuddin is an Alumnus of the University of Leeds
# Currently, he works as a Software Engineer at Sage (sage.com)
# Edited by Ammar Alsalka, University of Leeds, 2021
#------------------------------------------------------------------------------
import requests
import json
import re
import datetime

#-------------------------------------------------------------------------------
#   This is the client class which interacts with different news agencies and
#               provides the user with various API call options.
#-------------------------------------------------------------------------------
class Client():
    #Init function to set required class variables
    def __init__(self):
        self.s = requests.Session()
        self.url="None"
        self.status="None"


    #Login the user to a news agency if username, url, and password are valid
    def login(self, username, password):
        print("\nLoggin In....")
        payload = {'username': username, 'password': password}
        headers = {'content-type': 'application/x-www-form-urlencoded'}
		
        try:
            r = self.s.post(self.url+"api/login/", data=payload, headers=headers, timeout=4)
            print(r.text)
            print("Status Code is %s" % r.status_code)
            if(r.status_code==200):
                self.status="("+username+") "
            else:
                self.url = "None"
        except requests.exceptions.RequestException:
            print("Error! Failed to establish connection to:", self.url)
            self.url="None"


    #Logs the user out from current session if its active
    def logout(self):
        print("\nLoggin out....")
        try:
            r = self.s.post(self.url+"api/logout/",timeout=10)
            print(r.text)
            print("Status Code is %s"%r.status_code)
            if(r.status_code==200):
                self.status="None"
        except requests.exceptions.RequestException:
            print("Error! Failed to logout from ",self.url)


    #Sends a post request to add a news story to a news agency
    def postStory(self, headline, category, region, details):
        print("\nPosting Story....")
        headers = {'content-type': 'application/json'}
        payload = {'headline': headline, 'category': category, 'region':region, 'details': details}

        try:
            r = self.s.post(self.url+"api/poststory/",data=json.dumps(payload), headers=headers, timeout=10)
            print(r.text)
            print("Status Code is %s" % r.status_code)
        except requests.exceptions.RequestException:
            print("Error! Failed to post to ", self.url)


    # gets news stories from a single news agency
    def getSingleStories(self, params, agency=None):  # params: 0=id  1=cat   2=reg   3=date

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        payload = {'story_cat': params[1], 'story_region': params[2], 'story_date':params[3]}

        if(agency==None):
            agency=self.getAgency(params[0])
        if(agency=="Not Found"):
            print("Error! Could not find agency with unique code ", params[0])
            return

        url=agency["url"]
        if not url.startswith("http://"):
            url = "http://"+url
        if not url.endswith("/"):
            url = url+"/"

        try:
            r = self.s.get(url+"api/getstories/", data=json.dumps(payload), headers=headers, timeout=10)

            print("\nRetrieving News Stories from ",agency["agency_name"],"....")

            if(r.status_code==200):
                stories=json.loads(r.text)
                i=1
                for story in stories["stories"]:
                    print("\nStory ",i)
                    print("Key: ".ljust(20),story["key"])
                    print("Headline: ".ljust(20), story["headline"])
                    print("Category: ".ljust(20), story["story_cat"])
                    print("Region: ".ljust(20), story["story_region"])
                    print("Author Name: ".ljust(20), story["author"])
                    print("Date Published: ".ljust(20), story["story_date"])
                    print("Details: ".ljust(20), story["story_details"])
                    i+=1
            else:
                print("\n Error! Failed to retrieve stories from ", url)
                if(len(r.text)<=500):
                    print(r.text)
                print("Status Code is %s" % r.status_code)
        except Exception:
            print("\nError!  Failed to retrieve stories from ", url)


    #Gets news stories from all news agencies registered in the directory
    def getAllStories(self, params):
        print("\nGetting News Stories From All Agencies....")
        r = self.s.get('http://directory.pythonanywhere.com/api/list/', timeout=4)

        if(r.status_code==200):
            agencies=json.loads(r.text)
            for agency in agencies["agency_list"]:
                self.getSingleStories(params, agency=agency)
        else:
            print(r.text)
            print("Status Code is %s" % r.status_code)


    #Attempts to delete a story from a news agency
    def deleteStory(self, key):
        print("\nDeleting Story With Key:",key,"....")
        headers = {'content-type': 'application/json'}
        payload = {'story_key': key}

        try:
            r = self.s.post(self.url+"api/deletestory/",data=json.dumps(payload), headers=headers, timeout=10)
            print(r.text)
            print("Status Code is %s" % r.status_code)
        except requests.exceptions.RequestException:
            print("Error! Failed to delete story with key ", key)


    # initially, this should be used once to register your agency in the directory
	# insert your service details before calling this function
	# -------------------------------------------------------------------
    def registerService(self):
        print("\nRegistering Service....")
        headers = {'content-type': 'application/json'}
        payload = {"agency_name": "Enter your agency name here",
                   "url": "http://???.pythonanywhere.com/",
                   "agency_code":"???"}

        r = self.s.post('http://directory.pythonanywhere.com/api/register/',
                        data=json.dumps(payload), headers=headers, timeout=10)
        print(r.text)
        print("Status Code is %s" % r.status_code)


    #Lists all agencies registered in the directory
    def listAgencies(self):
        print("\nListing all agencies in the directory....")
        r = self.s.get('http://directory.pythonanywhere.com/api/list/', timeout=10)

        if(r.status_code==200):
            agencies=json.loads(r.text)
            i=1
            for agency in agencies["agency_list"]:
                print("\nAgency ",i)
                print("Name: ".ljust(35),agency["agency_name"])
                print("URL: ".ljust(35), agency["url"])
                print("Unique Code: ".ljust(35), agency["agency_code"])
                i+=1
        else:
            if(len(r.text)<=500):
                print(r.text)
            print("Status Code is %s" % r.status_code)


    #Given the 3 letter agency code, will find and return the agency object
    def getAgency(self, code):
        r = self.s.get('http://directory.pythonanywhere.com/api/list/', timeout=10)

        if(r.status_code==200):
            agencies=json.loads(r.text)
            for agency in agencies["agency_list"]:
                if(agency["agency_code"]==code):
                    return agency
        return "Not Found"

    #Prints out some welcome information
    def displayWelcome(self):
        print("\n\t\tWelcome To Amazing Client! Please enter your commands")
        print("Do not append to the url the api address e.g. api/login, this is automatically added")
        print("-------------------------------------------------------------------------------------")
        print("--) register (use once only to register your service)                                ")
        print("--) login url                                                                       -")
        print("--) logout                                                                          -")
        print("--) post                                                                            -")
        print("--) news [id def=*] [cat def=*] [reg def=*] [date def=*]                            -")
        print("--) list                                                                            -")
        print("--) delete story_key                                                                -")
        print("----exit (to stop client)                                                           -")
        print("----show (to display available commands)                                            -")
        print("-------------------------------------------------------------------------------------")


    #Client interface which processes the user's inputs
    def runClient(self):
        self.displayWelcome()
        while(True):
            if(self.status!="None"):
                prompt=self.status+">>>"
            else:
                prompt = ">>>"
            command=input(prompt).strip().split()

            if not command:                                         # empty
                continue
            if(command[0]== "register"):
                self.registerService ()				
            elif(command[0]=="login" and len(command)==2):            # login
                username = input("Please enter your username: ").strip()
                password = input("Please enter your password: ").strip()
                self.setURL(command[1])
                self.login(username, password)
            elif(command[0]=="logout" and len(command)==1):         # logout
                if(self.url=="None"):
                    print("Error! current session is not active, please login to a url for logout to work!")
                else:
                    self.logout()
            elif(command[0] == "post" and len(command) == 1):       # post
                if(self.url == "None"):
                    print("Error! not logged in, please login first using the login command")
                    continue
                self.processPostInput(command)
            elif(command[0] == "news"):                             # news
                self.processNewsInput(command)
            elif(command[0]=="list" and len(command)==1):           # list
                self.listAgencies()
            elif(command[0]=="delete" and len(command)==2 and command[1].isdigit()==True):      # delete
                if(self.url == "None"):
                    print("Error! not logged into any server, please login to a server using [login url]")
                    continue
                self.deleteStory(command[1])
            elif(command[0] == "exit"):                               # exit
                break
            elif(command[0]=="show" and len(command)==1):             # show
                self.displayWelcome()


    #Processes the post input from user and calls relevant class function
    def processPostInput(self, command):
        headline=input("Headline: ")
        category=""
        while(not (category=="pol" or category=="art" or category=="trivia" or category=="tech")):
            category=input("Category (pol, art, trivia, tech)")

        region=""
        while(not (region=="eu" or region=="w" or region=="uk")):
            region=input("Region (eu, w, uk)")
        details=input("Details: ")
        self.postStory(headline, category, region, details)


    #Processes the news input and calls relevant class functions
    def processNewsInput(self, command):
        params = ["*", "*", "*", "*"]  # 0=id  1=cat   2=reg   3=date
        for cmd in command[1:]:
            if(len(cmd) == 3 and cmd != "pol" and cmd != "art" and cmd.isalpha()):
                params[0] = cmd
            elif(cmd == "pol" or cmd == "art" or cmd == "tech" or cmd == "trivia"):
                params[1] = cmd
            elif(cmd == "uk" or cmd == "w" or cmd == "eu"):
                params[2] = cmd
            elif(len(cmd)==10):
                m = bool(re.match('^\d\d/\d\d/\d{4}$', cmd))  # dd/mm/yyyy
                if(self.checkDateIsValid(cmd) == True and m == True):
                    params[3] = cmd
                else:
                    return

        print("Final news: ", params)
        if(params[0]!="*"):
            self.getSingleStories(params)
        elif(params[0]=="*"):
            self.getAllStories(params)

    #Checks if the date provided is a valid date
    def checkDateIsValid(self, cmd):
        day, month, year = cmd.split('/')
        try:
            d=datetime.datetime(int(year), int(month), int(day))
            return True
        except ValueError:
            print("Error! date is not a valid date, plz try again")

        return False

    #Checks and corrects the url from the user and updates the class variable
    def setURL(self, url):
        if not url.startswith("http://"):
            url = "http://"+url
        if not url.endswith("/"):
            url = url+"/"
        print("final url: ", url)
        self.url=url

#Main function which simply creates a client and starts the interface
if __name__ == "__main__":
    c = Client()
    c.runClient()
