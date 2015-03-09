import whatsapp_analyse_head as head

import numpy as np
from datetime import datetime, timedelta

import plotly as py
from plotly.graph_objs import *
py.tools.set_credentials_file(username='jonasdb', api_key='2r0kiy0eq1', stream_ids=['fs43hhoxgj', '86nsdjyshj'])

#-------------------------------------------------------------------------#
#-------------------------------PARAMETERS--------------------------------#
#-------------------------------------------------------------------------#
outputMessagingPatterns = True
ana1 = ['Date', 'dayOfWeek', 'timeOfDay', 'weekHeatmap']
ana2 = ['raw', 'volumeProportion', 'personalProportion']
timeAnalysisType = [ana1[3], ana2[2]]

outputLanguageAnalysis = False
outputSpellingAccuracy = False

#-------------------------------------------------------------------------#
#-------------------------------------------------------------------------#

raw_text = open('WhatsApp Chat Log 19022015.txt', 'r')

wordCount = 0
numMessages = 0

lineArray = list(raw_text)
lineCount = len(lineArray)

#Create list of all messages, including multi-line ones
lines = head.SortLines(lineArray, lineCount)
numMessages = len(lines)

messageList = []
eventList = []
nameSet = set()

for line in lines:
	separated = line.split(' - ')
	if not separated[0][-4:].isdigit():
		separated[0] += " " + str(datetime.now().year)
	dateAndTime = datetime.strptime(separated[0], '%H:%M, %d %b %Y')
	date = dateAndTime
	nameAndMessage = separated[1].split(': ', 1)

	if "822133" in nameAndMessage[0]:
		nameAndMessage[0].replace("+44 7703 822133", "Octavian")

	if len(nameAndMessage) == 1:
		eventList.append(head.StoreEvent(nameAndMessage, separated, date))
	elif len(nameAndMessage) == 2:
		messageList.append(head.StoreMessage(nameAndMessage, date))
		if nameAndMessage[0] not in nameSet:
			nameSet.add(nameAndMessage[0])


if outputMessagingPatterns:
	head.MessagingPatternAnalysis(messageList, eventList, nameSet, timeAnalysisType)

if outputLanguageAnalysis:
	head.LanguageAnalysis(messageList, nameSet)

if outputSpellingAccuracy:
	head.SpellCheckConversation(messageList, nameSet, output='raw')


print numMessages
print wordCount
print "average message size = ", (1.0 * wordCount / numMessages)






