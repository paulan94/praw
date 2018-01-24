import praw
from collections import defaultdict
import csv
from multi_key_dict import multi_key_dict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import datetime
from datetime import timedelta


class paul_praw():
    
    #init reddit instance
    def __init__(self, subreddit_name, thread_limit):
        print ("Initializing for {} threads on subreddit: {}...".format(thread_limit, subreddit_name))
        self.reddit = praw.Reddit(client_id = 'GETTHISONREDDIT',
                             client_secret = 'GETTHISONREDDIT',
                             username='GETTHISONREDDIT',
                             password='GETTHISONREDDIT',
                             user_agent='GETTHISONREDDIT') #reddit instance

        self.subreddit = self.reddit.subreddit(subreddit_name)
        self.hot_python = self.subreddit.hot(limit=thread_limit) #some id looking thing
        self.coin_dict = multi_key_dict()
        self.analyzer = SentimentIntensityAnalyzer()


        #make separate searches for thread and comment count
        print ("Finished Initializing!")


    def create_coin_dict(self):
        print ("Creating coin dictionary data structure...")
        #use coinmarketcap api
        with open('coinmcapcoins.csv',newline='') as csvfile:
            coinreader = csv.reader(csvfile, delimiter=',')
            for row in list(coinreader):
##                print (row[0:3])
                #0 array definitions
                #thread mentions, comment mentions, neg thread, pos thread,
                #neg comment, pos comment, time
                self.coin_dict[row[0:3]] = [0,0,0,0,0,0,[]]
        print ("Finished creating coin dict!")

    #later can differentiate between thread,comments
    def sentiment_analysis(self, sentence, coin, is_comment):
        snt = self.analyzer.polarity_scores(sentence)
        #dict {'neg': 0.538, 'neu': 0.462, 'pos': 0.0, 'compound': -0.5423}
        #[neg,pos]
        if is_comment:
            if (snt['neg'] > snt['pos']): #increase number of negative mentions
                self.coin_dict[coin][4] += 1
            elif(snt['pos'] > snt['neg']): #increase number of positive mentions
                self.coin_dict[coin][5] += 1
        else: #found in thread
            if (snt['neg'] > snt['pos']): #increase number of negative mentions
                self.coin_dict[coin][2] += 1
            elif(snt['pos'] > snt['neg']): #increase number of positive mentions
                self.coin_dict[coin][3] += 1
        return


    def parse_threads(self):
        print ("Parsing threads...")
        for submission in self.hot_python:
            if not (submission.stickied):
                #use upvotes to weight 'submission.ups'
                #loop through dict keys and check if in submission title
                for coin_keys in list(self.coin_dict.keys()):
##                    coin = coin_keys[1] # do this is I want to search only the coins name (omitting the acronym
                    for coin in coin_keys[1:3]:
                        if (coin in submission.title.split()): #took out upper() for more precision
                            print ("found {} in title".format(coin))
                            self.coin_dict[coin][0] += 1
                            self.sentiment_analysis(str(submission.title),coin, False)
                            self.get_date(submission,coin)
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments.list():
                            encoded_comment = comment.body.encode("utf-8", errors='ignore')
                            if (coin in encoded_comment.decode().split()): #took out upper() for more precision
                                self.coin_dict[coin][1] += 1
                                self.sentiment_analysis(encoded_comment.decode(),coin, True)
        print ("Finished parsing!")



    def write_coin_dict(self):
        print ("Writing started...")
        sorted_dict = sorted(self.coin_dict.items(), key= lambda x: x[1], reverse=True)
        line_count = 0
        with open("results.txt", 'w') as file:
            for (k,v) in sorted_dict:
                if (v[0] > 1  or v[1] > 1):
                    line_count += 1
                    file.write("{} has been found {} times in a thread title, and {} times in a comment. Negative THREADS: {}. Positive THREADS: {}. Negative COMMENTS: {}. Positive COMMENTS: {}. Thread Creation Time: {} hours ago.\n".format(k,v[0],v[1],v[2],v[3],v[4],v[5],v[6]))
        print ("Successfuly wrote {} lines to results.txt".format(line_count))

    def get_date(self,submission,coin): #adds to coin_dict the time in hours since creation
        time = datetime.datetime.fromtimestamp(submission.created_utc)
        dif = (datetime.datetime.now() - time)
        hours_since_creation = (dif.total_seconds()/3600)
        #print (dif)
        
        self.coin_dict[coin][6].append(float("{0:.2f}".format(hours_since_creation)))
        return

def main():
    #run program
    p = paul_praw("cryptocurrency",50)
    p.create_coin_dict()
    p.parse_threads()
    p.write_coin_dict()
    

if __name__ == "__main__":
    main()

