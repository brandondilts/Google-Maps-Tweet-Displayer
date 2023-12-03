import tkinter
import math
import ssl
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode, quote_plus
import json

import sys
sys.path.insert(0,'./modulesForOauth')
import requests
from requests_oauthlib import OAuth1
from urllib.parse import quote_plus

#

GOOGLEAPIKEY = "AIzaSyAKo2owg7i2wwS0YnPmfGSa866yAWGARp8"

API_KEY = "sMdJaNxsNGYS2rPljqKmJOL2n"
API_SECRET = "pk1hjMPoeP53CtsVrOTDJWrqH7fwKbdHWHuQ5e0py8mTJ3Y6x2"
ACCESS_TOKEN = "1024806811-LHv3EvHztvWc2HIDpnkciKr9ahpkarATWfEMt2W"
ACCESS_TOKEN_SECRET = "qG27QjPHXSQYlvTUXHaOmbsg3PuaM2zulapsOmYG3l6ut"

#
class Globals:
   
   rootWindow = None
   mapLabel = None
##
   
   locationEntry = None   
   tweetTermEntry = None
   tweetText = None
   mapType= 'roadmap'  
   choiceVar = None
   client = None
   userNameLabel = None
   realNameLabel = None
   totalAmountofTweetsLabel = None
   totalAmountofTweets = 0
   tweetLocationList = []
   currentTweetIndex = 0
   tweets = []
   mapcenter = []
   finalMarkerString = ""
  

   defaultLocation = "Mauna Kea, Hawaii"
   mapLocation = defaultLocation
   mapFileName = 'googlemap.gif'
   mapSize = 400
   zoomLevel = 9
   
def authTwitter():    
    Globals.client = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
   

def increaseZoomBy1():    
    Globals.zoomLevel = Globals.zoomLevel + 1
    displayMap()
    
def decreaseZoomBy1():    
    
    if Globals.zoomLevel > 0:
        Globals.zoomLevel = Globals.zoomLevel - 1
    displayMap()
    
#Change Map Type
    
def radioButtonChosen():
    
    if Globals.choiceVar.get() == 1:        
        Globals.mapType = 'roadmap'
        
    if Globals.choiceVar.get() == 2:        
        Globals.mapType = 'satellite'
        
    if Globals.choiceVar.get() == 3:        
        Globals.mapType = 'terrain'
        
    if Globals.choiceVar.get() == 4:
        Globals.mapType = 'hybrid'
        
    displayMap()
    

        
    
       
   
def geocodeAddress(addressString):
   urlbase = "https://maps.googleapis.com/maps/api/geocode/json?address="
   geoURL = urlbase + quote_plus(addressString)
   geoURL = geoURL + "&key=" + GOOGLEAPIKEY

   # required (non-secure) security stuff for use of urlopen
   ctx = ssl.create_default_context()
   ctx.check_hostname = False
   ctx.verify_mode = ssl.CERT_NONE
   
   stringResultFromGoogle = urlopen(geoURL, context=ctx).read().decode('utf8')
   jsonResult = json.loads(stringResultFromGoogle)
   if (jsonResult['status'] != "OK"):
      print("Status returned from Google geocoder *not* OK: {}".format(jsonResult['status']))
      result = (0.0, 0.0) # this prevents crash in retrieveMapFromGoogle - yields maps with lat/lon center at 0.0, 0.0
   else:
      loc = jsonResult['results'][0]['geometry']['location']
      result = (float(loc['lat']),float(loc['lng']))
   return result



def getMapUrl():
   lat, lng = geocodeAddress(Globals.mapLocation)

   

   urlbase = "http://maps.google.com/maps/api/staticmap?"
   args = "center={},{}&zoom={}&size={}x{}&maptype={}&format=gif".format(lat,lng,Globals.zoomLevel,Globals.mapSize,Globals.mapSize,Globals.mapType)
   args = args + Globals.finalMarkerString + "&key=" + GOOGLEAPIKEY
   mapURL = urlbase + args 
   
   return mapURL

def retrieveMapFromGoogle():
   url = getMapUrl()
   urlretrieve(url, Globals.mapFileName)
   
def printable(s):
    result = ''
    for c in s:
        result = result + (c if c <= '\uffff' else '?')
    return result


########## 
#  basic GUI code

def displayMap():
#  added bit to keep zoom level when changing map type
   Globals.zoomLevel = Globals.zoomLevel 

   retrieveMapFromGoogle()    
   mapImage = tkinter.PhotoImage(file=Globals.mapFileName)
   Globals.mapLabel.configure(image=mapImage)
   # next line necessary to "prevent (image) from being garbage collected" - http://effbot.org/tkinterbook/label.htm
   Globals.mapLabel.mapImage = mapImage
   
def displayTweet():
    currentTweet = Globals.tweets[Globals.currentTweetIndex]
    currentTweetText = printable(currentTweet['text'])
    currentTweetScreenName = currentTweet['user']['screen_name']
    currentTweetRealName = currentTweet['user']['name']
    
    Globals.totalAmountofTweetsLabel.configure(text="Total Tweets:" +  str(Globals.totalAmountofTweets))
    Globals.userNameLabel.configure(text="Screen Name: @" + currentTweetScreenName)
    Globals.realNameLabel.configure(text="Real Name: " + currentTweetRealName)
    Globals.tweetText.configure(state=tkinter.NORMAL)
    Globals.tweetText.delete(1.0, tkinter.END)
    Globals.tweetText.insert(1.0, currentTweetText)
    Globals.tweetText.configure(state=tkinter.DISABLED)
    
    
    
    
    

###Get marker parts###
def generateMarkerString(currentIndex, tweetLatLonList, mapCenterLatLon):
    otherIndex = 0
    #print('in generate marker current index' + str(currentIndex))
    #print('in gen latlong list len' + str(len(tweetLatLonList)))
    if tweetLatLonList[currentIndex] == None:
        markerString =  "&markers=color:red|{}".format(mapCenterLatLon)
        
    else:
        
        markerString =  "&markers=color:red|{}".format(tweetLatLonList[currentIndex]['coordinates'])
        
    #print(mapCenterLatLon)
    #print(markerString)
    
   
     
    first = 0
    while otherIndex < len(tweetLatLonList):
        if otherIndex !=currentIndex:
            if first == 0:
                if tweetLatLonList[otherIndex] == None:                   
                    markerString = markerString + ("&markers=color:blue|size:small|{}".format(mapCenterLatLon))                                              
                else:
                   #print(type(tweetLatLonList[otherIndex]['coordinates']))
                    
                   #print('i am in the else')
                   # tweetLatLonList[otherIndex]['coordinates'] = reverseCoordinates(tweetLatLonList[otherIndex]['coordinates'])
                    markerString = markerString + ("&markers=color:blue|size:small|{}".format(tweetLatLonList[otherIndex]['coordinates']))
                first = 1    
            else:
                if tweetLatLonList[otherIndex] == None:
                    markerString = markerString + ("|{}".format(mapCenterLatLon))
                else:
                    
                    markerString = markerString + ("|{}".format(tweetLatLonList[otherIndex]['coordinates']))                                  
                                                    
        otherIndex = otherIndex + 1
    
    
    Globals.finalMarkerString = ""
    for char in markerString:
        if char != '[':
            if char != ']':
                if char != ' ':
                    Globals.finalMarkerString = Globals.finalMarkerString + char
    #print(Globals.finalMarkerString)
           
 
#####

def finalgenerateMarkerString():
    
    generateMarkerString(currentIndex = Globals.currentTweetIndex, tweetLatLonList= Globals.tweetLocationList, mapCenterLatLon = Globals.mapcenter)
    
    
    
   
def searchTwitter(searchString, count = 20, radius = 2, latlngcenter = None):
    Globals.currentTweetIndex = 0
  #  Globals.tweets = []    
  #  Globals.tweetLocationList = []
    Globals.totalAmountofTweets = 0
    
    query = "https://api.twitter.com/1.1/search/tweets.json?q=" + quote_plus(searchString) + "&count=" + str(count)
    
    if latlngcenter != None:
        query = query + "&geocode=" + str(latlngcenter[0]) + "," + str(latlngcenter[1]) + "," + str(radius) + "km"
    global response
    response = requests.get(query, auth=Globals.client)
    resultDict = json.loads(response.text)
    # The most important information in resultDict is the value associated with key 'statuses'
    Globals.tweets = resultDict['statuses']
 
    
    for tweetIndex in range(len(Globals.tweets)):
        Globals.totalAmountofTweets = Globals.totalAmountofTweets + 1
        
        #tweet = Globals.tweets[tweetIndex]
        #locationCoor = tweet['coordinates']
        Globals.tweetLocationList.append(Globals.tweets[tweetIndex]['coordinates'])
    
    #print(Globals.tweetLocationList)    
    index = 0
    while index < len(Globals.tweetLocationList):
        if Globals.tweetLocationList[index] != None:
            #print(Globals.tweetLocationList[index]['coordinates'])
            Globals.tweetLocationList[index]['coordinates'].reverse()
            #print(Globals.tweetLocationList[index]['coordinates'])
        index = index + 1
                
        
    ##print(t0['text'])
    #print(Globals.tweetLocationList)
    #print(Globals.tweetLocationList[1]['coordinates'])
    #print(Globals.totalAmountofTweets)
    
    return Globals.tweets

   
def readEntriesSearchTwitterAndDisplayMap():
   
   Globals.tweetLocationList = []
   
   locationString = Globals.locationEntry.get()   
   Globals.mapLocation = locationString
   
   tweetString= Globals.tweetTermEntry.get()
   searchString = tweetString
   lat, lng =geocodeAddress(Globals.mapLocation)
   Globals.mapcenter = [lat, lng]
   
   searchTwitter(searchString, count = 20, radius = 2, latlngcenter = Globals.mapcenter)
   finalgenerateMarkerString()
   displayTweet()
   displayMap()
   
def nextTweet():
    if Globals.currentTweetIndex < (Globals.totalAmountofTweets - 1):
        Globals.currentTweetIndex = Globals.currentTweetIndex + 1
    finalgenerateMarkerString()
    displayTweet()
    displayMap()
    
def previousTweet():
    if Globals.currentTweetIndex > 0:
        Globals.currentTweetIndex = Globals.currentTweetIndex - 1
    finalgenerateMarkerString()
    displayTweet()
    displayMap()
   
     
def initializeGUIetc():
    
   

   Globals.rootWindow = tkinter.Tk()
   Globals.rootWindow.title("HW9")
   
   Globals.choiceVar = tkinter.IntVar()
   Globals.choiceVar.set(1)

   mainFrame = tkinter.Frame(Globals.rootWindow) 
   mainFrame.pack()
   
   tweetFrame = tkinter.Frame()
   tweetFrame.pack(side=tkinter.BOTTOM)
      
   #entry
   label1 = tkinter.Label(mainFrame, text="Enter the location: ")
   label1.pack(side=tkinter.TOP)
   Globals.locationEntry = tkinter.Entry(mainFrame)
   Globals.locationEntry.pack(side=tkinter.TOP)
   
   label2 = tkinter.Label(mainFrame, text="Enter the Tweet term: ")
   label2.pack(side=tkinter.TOP)
   Globals.tweetTermEntry = tkinter.Entry(mainFrame)
   Globals.tweetTermEntry.pack(side=tkinter.TOP)
   
   
   
   #zoom
   decreaseButton = tkinter.Button(mainFrame, text="-", command=decreaseZoomBy1)
   decreaseButton.pack(side=tkinter.BOTTOM)
   increaseButton = tkinter.Button(mainFrame, text="+", command=increaseZoomBy1)
   increaseButton.pack(side=tkinter.BOTTOM)
   
   
   #mapstyle
   choice1 = tkinter.Radiobutton(mainFrame, text="roadmap", variable=Globals.choiceVar, value=1,command=radioButtonChosen)
   choice1.pack(side=tkinter.RIGHT)
   choice2 = tkinter.Radiobutton(mainFrame, text="satellite", variable=Globals.choiceVar, value=2,command=radioButtonChosen)
   choice2.pack(side=tkinter.RIGHT)
   choice3 = tkinter.Radiobutton(mainFrame, text="terrain", variable=Globals.choiceVar, value=3,command=radioButtonChosen)
   choice3.pack(side=tkinter.RIGHT)
   choice4 = tkinter.Radiobutton(mainFrame, text="hybrid", variable=Globals.choiceVar, value=4,command=radioButtonChosen)
   choice4.pack(side=tkinter.RIGHT)
  
    
##tweet display   
   tweetInfo = tkinter.Label(tweetFrame, text="Tweet Info:")
   tweetInfo.pack()
   
   Globals.totalAmountofTweetsLabel =tkinter.Label(tweetFrame, text="Total Tweets: no tweets yet")
   Globals.totalAmountofTweetsLabel.pack()
   
   Globals.userNameLabel =tkinter.Label(tweetFrame, text="Screen Name:")
   Globals.userNameLabel.pack()
   
   Globals.realNameLabel =tkinter.Label(tweetFrame, text="Real Name:")
   Globals.realNameLabel.pack()
   
   Globals.tweetText = tkinter.Text(tweetFrame, width = 72, height = 3, bd = 2) 
   Globals.tweetText.insert(1.0, "Tweet goes here")                         
   Globals.tweetText.configure(state=tkinter.DISABLED)                       
   Globals.tweetText.pack()
   
   nextTweetButton = tkinter.Button(tweetFrame, text="Next Tweet", command= nextTweet)
   nextTweetButton.pack(side = tkinter.RIGHT)
   
   previousTweetButton = tkinter.Button(tweetFrame, text="Previous Tweet", command= previousTweet)
   previousTweetButton.pack(side = tkinter.LEFT)
   
   
   
 
#####  
   readEntriesSearchTwitterAndDisplayMapButton = tkinter.Button(mainFrame, text="Search Twitter and Display Map!", command=readEntriesSearchTwitterAndDisplayMap)
   readEntriesSearchTwitterAndDisplayMapButton.pack(side=tkinter.TOP)

   # we use a tkinter Label to display the map image
   Globals.mapLabel = tkinter.Label(mainFrame, width=Globals.mapSize, bd=2, relief=tkinter.FLAT)
   Globals.mapLabel.pack()

def HW9():
    authTwitter()
    initializeGUIetc()
    displayMap()
    Globals.rootWindow.mainloop()
