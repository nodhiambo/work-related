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
####################################################################################### 
def processURL(myUrl):
  strBuild = ""
  try:
    # Parse url
    feeds = feedparser.parse(myUrl)
    print("Please wait for processing to be completed. It may take several minutes...")
    print ("URL of the feed: "+myUrl)
    print ("Total entries: "+str(len(feeds['entries'])))
    #print ("URL of the feed: "+feeds['feed']['link'])
    errorMsg = "There is no entry description or summary"
    for post in feeds.entries:
      print("\n")
      print("Feed Title: "+post.title)
      print("URL of the individual entry: "+post.link+"\n")
      try:
        if post.description != None or post.summary != None:
          if post.description:
            #obtain only individual entries
            try:
              soup = BeautifulSoup(post.description)
              soup = soup.findAll(text=True)
              # Remove all the endlines from the sentences
              cleansed = [a for a in soup if a != '\n']
              # Remove preceding u' from all the sentences aka encoding
              encoded =  [x.encode('utf-8') for x in cleansed]
              for text in encoded:
                if text:
                  strBuild += text 
              #Remove ending spaces      
              if strBuild.endswith('  '):
                strBuild = strBuild[:-4]      
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
              encoded =  [x.encode('utf-8') for x in cleansed]
              for text in encoded:
                if text:
                  strBuild += text 
              #Remove ending spaces      
              if strBuild.endswith('  '):
                strBuild = strBuild[:-4]   
            except Exception, e:
              print (str(e))    
        else:
           print(errorMsg)
      except Exception, e:
        print (str(e))  
      strBuild = cleanhtml(strBuild) 
      processEntrySentiment(strBuild, errorMsg)  
      # Initialize string and array
      strBuild = ""    
  except Exception, e:
    print (str(e))  
  return

######################################################################################
# Process for each entry:
# 3. Sentiment expressed in the entry's text This should have the following format:
#    - positive indicators: [list of positive indicators]
#    - negative indicators: [list of negative indicators]
#    - overall sentiment: <"positive"|"negative"|"neutral"> 
#######################################################################################    
def processEntrySentiment(strText, msg):
  negCount = 0
  posCount = 0
  posList = []
  negList = []
  sentenceArray = [] 
  if strText:  
    text = TextBlob(strText)
    count = 0                 
    for sentence in text.sentences:
        sentenceArray.append(str(sentence))
        blob = TextBlob(str(sentence), analyzer=NaiveBayesAnalyzer())
        if blob.sentiment.classification == 'neg':
          negCount += 1
          negList.append(str(sentence))
        else:
          posCount += 1
          posList.append(str(sentence))   
    
    # Another module sentiment indicator to confirm results by comparison 
    pos_score, neg_score = senti_classifier.polarity_scores(sentenceArray)
    print ("Comparative Positive score: "+str(pos_score))
    print ("Comparative Negative score: "+str(neg_score))
     
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
  else:
    print(msg)
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
   
  