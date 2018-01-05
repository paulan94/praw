import praw
from collections import defaultdict
import csv
from multi_key_dict import multi_key_dict



######### CHANGE USERNAME AND PASSWORD TO RUN! ########

class paul_praw():
    
    #init reddit instance
    def __init__(self, subreddit_name, thread_limit):
        print ("Initializing...")
        ######### CHANGE USERNAME AND PASSWORD TO RUN BELOW! ########
        # https://www.reddit.com/prefs/apps/ create app there to get info below
        
        self.reddit = praw.Reddit(client_id = 'UPDATE CLIENT ID',
                             client_secret = 'GET CLIENT SECRET FROM WEBSITE',
                             username='REDDIT_USER',
                             password='YOURPASSWORD',
                             user_agent='GET USER AGENT FROM WEBSITE') #reddit instance

        self.subreddit = self.reddit.subreddit(subreddit_name)
        self.hot_python = self.subreddit.hot(limit=thread_limit) #some id looking thing
        self.coin_dict = multi_key_dict()
        #make separate searches for thread and comment count
        print ("Finished Initializing!")


    def create_coin_dict(self):
        print ("Creating coin dictionary data structure...")
        #coin list taken from https://github.com/crypti/cryptocurrencies
        with open('allcoins.csv', newline='') as csvfile:
            coinreader = csv.reader(csvfile, delimiter=',')
            for row in list(coinreader):
                self.coin_dict[row] = 0
        print ("Finished creating coin dict!")



    def parse_threads(self):
        print ("Parsing threads...")
        for submission in self.hot_python:
            if not (submission.stickied):
##                print ('Title: {}, ups: {}, downs: {}, Have we visited: {}'.format(submission.title,
##                                                                                   submission.ups,
##                                                                                   submission.downs,
##                                                                                   submission.visited))
                #loop through dict keys and check if in submission title
                for coin_keys in self.coin_dict.keys():
                    for coin in coin_keys:
                        if (coin in submission.title.upper().split()):
                            print ("found {} in title".format(coin))
                            self.coin_dict[coin] += 1
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments.list():
                            encoded_comment = comment.body.encode("utf-8", errors='ignore')
                            if (coin in encoded_comment.decode().upper().split()):
                                self.coin_dict[coin] += 1
        print ("Finished parsing!")




    def print_coin_dict(self):

        print ("Printing started...")
        sorted_dict = sorted(self.coin_dict.items(), key= lambda x: x[1], reverse=True)
        for (k,v) in sorted_dict:
            if (v > 1):
                print ("{} has been found {} times. ".format(k,v))


def main():
    #run program
    p = paul_praw("cryptocurrency",5)
    p.create_coin_dict()
    p.parse_threads()
    p.print_coin_dict()
    

if __name__ == "__main__":
    main()

