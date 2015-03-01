import re, string, operator

import plotly as py
from plotly.graph_objs import *
py.tools.set_credentials_file(username='jonasdb', api_key='2r0kiy0eq1', stream_ids=['fs43hhoxgj', '86nsdjyshj'])

class Message:
	def __init__(self, date, name, message):
		self.date = date
		self.name = name
		self.message = message

class Event:
	def __init__(self, date, name, eventType, eventDetail):
		self.date = date
		self.name = name
		self.eventType = eventType
		self.eventDetail = eventDetail

def SortLines(lineArray, lineCount):
	lines = []

	for i, line in enumerate(lineArray):
		#check is start of new message line, not continuation of one
		if '-' in line[13:20]:

			#Consolidate multi-line messages
			j = 1
			combineLine = line
			while (i+j) < (lineCount) and not lineArray[i+j][0:2].isdigit():

				combineLine += " " + lineArray[i+j]
				j += 1

			lines.append(combineLine)
	return lines

def StoreMessage(nameAndMessage, date):
	name = nameAndMessage[0]
	message = nameAndMessage[1]

	return Message(date, name, message)

def StoreEvent(nameAndMessage, separated, date):
	if 'changed the subject' in nameAndMessage[0]:
		eventType = 'subject change'
		name = separated[1].split(' changed ')[0]
		eventDetail = separated[1].split('to ')[1][3:-4]

		return Event(date, name, eventType, eventDetail)
		

	elif 'added' in nameAndMessage[0]:
		preName = nameAndMessage[0].split(' added')[0].split(' ', 2)
		name = preName[0] + " " + preName[1]

		if 'was' in nameAndMessage[0] or 'were' in nameAndMessage[0]:
			eventType = 'was added'
		else:
			eventType = 'added'

		eventDetail = ''

		return Event(date, name, eventType, eventDetail)
		

	elif 'removed' in nameAndMessage[0]:
		splitText = nameAndMessage[0].split(' removed')[0]
		name = splitText[0]
		eventType = 'removal'
		eventDetail = splitText[1][1:]

		return Event(date, name, eventType, eventDetail)

def MessagingPatternAnalysis(messageList, eventList, nameSet, analysisType):
	firstDate = messageList[0].date.date()
	lastDate = messageList[len(messageList)-1].date.date()
	days = (lastDate - firstDate).days

	x = [0] * int(days)
	rowTemplate = dict.fromkeys(nameSet, 0)
	xPerName = [dict(rowTemplate) for k in range(days)]
	daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

	timeX = [0] * 24
	timeXPerName = rowTemplate = dict.fromkeys(nameSet, 0)
	timeXPerName = [dict(rowTemplate) for k in range(0, 24)]

	for message in messageList:
		#SORT BY DATE/day/month
		index = (int((message.date.date() - firstDate).days) % 7)
		x[index] += 1
		xPerName[index][message.name] += 1

		#Sort by time of day
		timeIndex = message.date.hour - 1
		timeX[timeIndex] += 1
		timeXPerName[timeIndex][message.name] += 1

	if analysisType[0] == 'Date':
		fig = AnalyseByDate(messageList, eventList, nameSet, analysisType, days, x, xPerName)
	elif analysisType[0] == 'dayOfWeek':
		fig = AnalyseByDate(messageList, eventList, nameSet, analysisType, days, x, xPerName, daysOfWeek)
	elif analysisType[0] == 'timeOfDay':
		fig = AnalyseByTime(messageList, eventList, nameSet, analysisType, days, timeX, timeXPerName)


	unique_url = py.plotly.plot(fig, filename=fig['layout']['title'])

		

def AnalyseByDate(messageList, eventList, nameSet, analysisType, days, x, xPerName, daysOfWeek):
	traces = []
	if analysisType[1] == 'raw':
		numberOfWeeks = int(days / 7)
		oneTrace = Scatter(x=daysOfWeek, y=[(x[index]/numberOfWeeks) for index in range(0, len(daysOfWeek))], name='Total')

		traces.append(oneTrace)
		for name in nameSet:
			oneTrace = Scatter(x=daysOfWeek, y=[(xPerName[index][name]/numberOfWeeks) for index in range(0, len(daysOfWeek))], name=name[:5])
			traces.append(oneTrace)
		layout = Layout(
	    	title='How many Messages Each Person Sends Each Day On Average',
	    	xaxis=XAxis(title='Day of the Week'),
	    	yaxis=YAxis(title='Number of Messages')
	    	)
	elif analysisType[1] == 'volumeProportion':
		for name in nameSet:
			oneTrace = Scatter(x=daysOfWeek, y=[(xPerName[index][name]*1.0/x[index]) for index in range(0, len(daysOfWeek))], name=name[:5])
			traces.append(oneTrace)
		layout = Layout(
	    	title='How Much of The Conversation Does Each Person Contribute?',
	    	xaxis=XAxis(title='Day of the Week'),
	    	yaxis=YAxis(title='Proportion of Daily Messages')
	    	)
	elif analysisType[1] == 'personalProportion':
		personTotalDay = dict.fromkeys(nameSet, 0)
		for index in range(0, 24):
			for name in nameSet:
				personTotalDay[name] += xPerName[index][name]
		for name in nameSet:
			oneTrace = Scatter(x=daysOfWeek, y=[(xPerName[index][name]*1.0/personTotalDay[name]) for index in range(0, len(daysOfWeek))], name=name[:5])
			traces.append(oneTrace)
		layout = Layout(
	    	title='When Are People Most Active?',
	    	xaxis=XAxis(title='Day of the Week'),
	    	yaxis=YAxis(title='Personal Proportion Weekly of Messages')
	    	)
	else:
		print "invalid analysis part 2 type"

	data = Data(traces)
	fig = Figure(data=data, layout=layout)

	return fig

def AnalyseByTime(messageList, eventList, nameSet, analysisType, days, timeX, timeXPerName):
	timeTraces = []
	if analysisType[1] == 'raw':
		timeTotalTrace = Scatter(x=[(str(a) + ":00") for a in range(0, 24)], y=[timeX[timeIndex] for timeIndex in range(0, 24)], name='Total')
		timeTraces.append(timeTotalTrace)
		for name in nameSet:
			oneTrace = Scatter(x=[(str(a) + ":00")  for a in range(0, 24)], y=[(timeXPerName[timeIndex][name]) for timeIndex in range(0, 24)], name=name[:5])
			timeTraces.append(oneTrace)

		layout = Layout(
		    title='What Time People Tend to Send Messages',
		    xaxis=XAxis(title='Time'),
		    yaxis=YAxis(title='Number of Total Messages')
		    )
	elif analysisType[1] == 'volumeProportion':
		for name in nameSet:
			oneTrace = Scatter(x=[(str(a) + ":00")  for a in range(0, 24)], y=[(timeXPerName[timeIndex][name]*1.0/timeX[timeIndex]) for timeIndex in range(0, 24)], name=name[:5])
			timeTraces.append(oneTrace)

		layout = Layout(
		    title='What Proportion of Messages a Person Provides Throughout the Day',
		    xaxis=XAxis(title='Time'),
		    yaxis=YAxis(title='Proportion of Daily Total Messages')
		    )
	elif analysisType[1] == 'personalProportion':
		personTotalTime = dict.fromkeys(nameSet, 0)
		for timeIndex in range(0, 24):
			for name in nameSet:
				personTotalTime[name] += timeXPerName[timeIndex][name]
		for name in nameSet:
			oneTrace = Scatter(x=[(str(a) + ":00")  for a in range(0, 24)], y=[(timeXPerName[timeIndex][name]*1.0/personTotalTime[name]) for timeIndex in range(0, 24)], name=name[:5])
			timeTraces.append(oneTrace)

		layout = Layout(
		    title='At What Time of Day is Each Person Most Active?',
		    xaxis=XAxis(title='Time'),
		    yaxis=YAxis(title='Proportion of Person\'s Total Messages')
		    )
	else:
		print "invalid analysis part 2 type"

	data = Data(timeTraces)
	fig = Figure(data=data, layout=layout)

	return fig

def LanguageAnalysis(messageList, nameSet):

	wordCatalogue = {}

	table = string.maketrans("","")
	for message in messageList:

		messageWords = message.message
		messageWords.translate(table, string.punctuation)
		messageWordsList = messageWords.split(' ')

		for word in messageWordsList:
			justWords = word.rstrip()
			lowerCaseWord = justWords.lower()

			if lowerCaseWord in wordCatalogue:
				wordCatalogue[lowerCaseWord] += 1
			else:
				wordCatalogue[lowerCaseWord] = 1

		#print wordCatalogue

	sortedWordCatalogue = sorted(wordCatalogue.items(), key=operator.itemgetter(1))

	for word in sortedWordCatalogue:
		print word













