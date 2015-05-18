#!/usr/bin/python

import sys, feedparser, feedfinder, requests, re
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from bs4 import BeautifulSoup
from senti_classifier import senti_classifier

# Cleanse the feed entry description by removing tags : <a>,<i> e.t.c
def cleanhtml(raw_html):
   cleanr = re.compile('<.*?>')
   cleantext = re.sub(cleanr,'', raw_html)
   return cleantext

######################################################################################
# Process the feed url by
# Display the URL of the feed
# For each entry (such as individual blog posts or news stories) in the feed display:
# 1. Title
# 2. URL
# 3. Sentiment expressed in the entry's text This should have the following format:
#    - positive indicators: [list of positive indicators]
#    - negative indicators: [list of negative indicators]
#    - overall sentiment: <"positive"|"negative"|"neutral"> 
####################################################################################### 
def processURL(myUrl):
    negCount = 0
    posCount = 0
    posList = []
    negList = []
    sentenceArray = []
    strBuild = ""
    try:
      # Parse url
      feeds = feedparser.parse(myUrl)
      print ("Total entries: "+str(len(feeds['entries'])))
      #print ("URL of the feed: "+feeds['feed']['link'])
      print ("URL of the feed: "+myUrl)
      for post in feeds.entries:
        print("Feed Title: "+post.title+"\n")
        print("Feed URL: "+post.link+"\n")
        try:
          if post.description or post.summary:
            if post.description:
              #obtain only individual entries
              try:
                soup = BeautifulSoup(post.description)
                soup = soup.findAll(text=True)
                # Remove all the endlines from the sentences
                cleansed = [a for a in soup if a != '\n']
                # Remove preceding u' from all the sentences aka encoding
                encodedArray =  [x.encode('utf-8') for x in cleansed]
                for text in cleansed:
                  strBuild += cleanhtml(text) 
              except Exception, e:
                print (str(e))      
            else:
              # If there is no entry description and there is a summary 
              try:
                soup = BeautifulSoup(post.summary)
                soup = soup.findAll(text=True)
                # Remove all the endlines from the sentences
                cleansed = [a for a in soup if a != '\n']
                # Remove preceding u' from all the sentences aka encoding
                encodedArray =  [x.encode('utf-8') for x in cleansed]
                for text in cleansed:
                  strBuild += cleanhtml(text) 
              except Exception, e:
                print (str(e))        
          else:
             print("There are no entry descriptions or summary")
        except Exception, e:
          print (str(e))  
         
      print("Please wait for the processing to be completed. It may take several minutes...")  
      text = TextBlob(strBuild)
      count = 0                 
      for sentence in text.sentences:
        if count < 5:    #Process only five sentences to shorten the processing time
          #sentenceArray.append(str(sentence))
          blob = TextBlob(str(sentence), analyzer=NaiveBayesAnalyzer())
          if blob.sentiment.classification == 'neg':
            negCount += 1
            negList.append(str(sentence))
          else:
            posCount += 1
            posList.append(str(sentence))
          count += 1   
          print("Processing sentence: "+str(count))
      
      # Another module sentiment indicator to confirm results by comparison 
      # pos_score, neg_score = senti_classifier.polarity_scores(sentenceArray)
      # print (pos_score, neg_score)
      
      print ("Negative Indicators: ")    
      print (negList)
      print ("Positive Indicators: ")
      print (posList)
      if negCount == posCount:                                                                    
        print ("Overall Sentiment: Neutral")
      else:
        if negCount > posCount:
          print ("Overall Sentiment: Negative")
        else:
          print ("Overall Sentiment: Positive")  
    except Exception, e:
      print (str(e))
      
    return  
      
# Get the total number of args passed
total = len(sys.argv)
if total != 2:
  print('Usage: Wrong number of arguments! Only one argument required.')
else:
  try:
    url = sys.argv[1]
    response = requests.get(url)
    if "text/html" in response.headers["content-type"]:
      #Examine the HTML source at the URL for syndication feeds (ATOM or RSS) : using feedfinder
      print('Obtaining the URL for the syndication feeds...')
      newFeedUrl = feedfinder.feed(url)
      if newFeedUrl:
        processURL(newFeedUrl)
      else:
        print ("No syndication feeds found.")
        sys.exit()
    else:
      processURL(url)  
           
  except Exception, e:
      print (str(e))
   
  