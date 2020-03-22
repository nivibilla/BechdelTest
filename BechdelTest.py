from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import urllib.request
import urllib.parse
import json
import matplotlib.pyplot as plot
import numpy as np


def getActionFilmNames():
	"""
	This method writes file in 'data' folder in working directory named 'title.txt' which contains the html for the rss
	feed provided by the website, from which the script url is taken.
	:return: list of Action Film Names, e.g.: ['15 Minutes', '48 Hrs.', ...]
	"""

	# The html file was taken from https://www.imsdb.com/genre/Action
	# Using the BeautifulSoup4 module to parse the html
	with open("./Data/ActionFilms.html") as fp:
		soup = BeautifulSoup(fp, 'lxml')
	listOfActionFilms = []

	# Finds all the links to the scripts
	for link in soup.findAll('a'):
		MovieName = link.get('title').replace("Script", "").strip()
		MovieName = MovieName.replace("\n", "").strip()
		MovieName = MovieName.replace("\r", "").strip()
		MovieName = MovieName.replace("\t", " ").strip()
		# removes the 'script' at the end and just appends name of movie to list
		listOfActionFilms.append(MovieName)

	# Writes scripts to data folder
	for film in listOfActionFilms:
		print("Writing RSS for " + film)
		# chrome_options = Options()
		# chrome_options.add_argument("--headless")
		# driver = webdriver.Chrome(options=chrome_options)
		# driver.get("https://www.imsdb.com/feeds/fromtitle.php?title=" + urllib.parse.quote(film))
		# with open("./Data/" + film + "RSS.txt", "w") as f:
		# 	f.write(driver.page_source)
		# driver.quit()

	return listOfActionFilms


def getFilmScripts(filmList):
	"""
	This method gets the scripts from the imsdb website, and writes it to a file in the data folder.
	:param filmList: list of film names, either manually given or by the method getActionFilmNames()
	:return: list of file names for the scripts e.g.: ['15 Minutes Script', '48 Hrs. Script', ...]
	"""
	scriptList = []
	for film in filmList:
		print("Writing Script for: " + film)
		# with open("./Data/" + film + "RSS.txt") as fp:
		# 	soup = BeautifulSoup(fp, 'lxml-xml')
		#
		# urlL = ""
		# for link in soup.findAll('item'):
		# 	urlLink = str(link.contents[len(link.contents) - 2].string)
		# 	urlL = urlLink
		#
		# chrome_options = Options()
		# chrome_options.add_argument("--headless")
		# driver = webdriver.Chrome(options=chrome_options)
		# driver.get(urlL)
		# with open("./Data/" + film + " Script.txt", "w") as f:
		# 	f.write(driver.page_source)
		# driver.quit()
		scriptList.append(film + " Script")

	return scriptList


def generateTestData(scriptList):
	"""
	This method returns a list of tuples with the first element being the movie name and the second, the list of pairs
	of character genders to be tested.
	:param scriptList: List of file names for the scripts as they are stored in the data folder
	 e.g.: 'Abyss, The Script.txt'
	:return: List of tuples, containing the name of the movie and the gender pairs.
	e.g.: ['Abyss, The', ['1,1', '2,1', ...]
	"""
	testData = []
	for script in scriptList:
		print("Testing movie: " + script.replace("Script", "").strip())
		with open("./Data/" + script + ".txt") as fp:
			soup = BeautifulSoup(fp, 'lxml')

		pairsOfCharacters = []
		pair = []
		for character in soup.findAll('b'):
			if len(pair) == 0:
				pair.append(str(character.string).strip())
			elif len(pair) == 1:
				pair.append(str(character.string).strip())
				pairsOfCharacters.append(pair)
				pair = [str(character.string).strip()]

		# name to search for
		movieName = script.replace(" Script", "")
		# using TMDB api get name of movie
		url = "https://api.themoviedb.org/3/search/multi?api_key=e98b5560d046220bdea14514aceb3483&query=" \
		      + urllib.parse.quote(movieName)
		# get closest matching movie data from url
		data = urllib.request.urlopen(url).read().decode()

		# parse data into json object
		jsonObj = json.loads(data)

		# get movie id
		if jsonObj["total_results"] != 0:
			movieID = str(jsonObj["results"][0]["id"]).strip()
		else:
			break

		# using TMDB api get cast of movie
		url = "https://api.themoviedb.org/3/movie/" + movieID + "/credits?api_key=e98b5560d046220bdea14514aceb3483"
		# get cast from url response
		data = urllib.request.urlopen(url).read().decode()

		# parse data into json object
		jsonObj = json.loads(data)

		# get cast details including, character name, actor/actress name, and gender
		cast = []
		for castMember in jsonObj["cast"]:
			cast.append([str(castMember["character"]), str(castMember["gender"]), str(castMember["name"])])

		# match the character name according to tmdb compared to what we are given in the script from imsdb
		for x in range(len(pairsOfCharacters)):
			for castMember in cast:
				if fuzz.partial_token_set_ratio(pairsOfCharacters[x][0].lower(), castMember[0].lower()) > 70:
					pairsOfCharacters[x] = [castMember[1], pairsOfCharacters[x][1]]
					break
				elif castMember[0].lower() == "himself" or castMember[0].lower() == "herself":
					if fuzz.partial_token_set_ratio(pairsOfCharacters[x][0].lower(), castMember[2].lower()) > 70:
						pairsOfCharacters[x] = [castMember[1], pairsOfCharacters[x][1]]
						break
				elif fuzz.partial_token_set_ratio(pairsOfCharacters[x][0].lower(), castMember[2].lower()) > 90:
					pairsOfCharacters[x] = [castMember[1], pairsOfCharacters[x][1]]
					break
			for castMember in cast:
				if fuzz.partial_token_set_ratio(pairsOfCharacters[x][1].lower(), castMember[0].lower()) > 70:
					pairsOfCharacters[x] = [pairsOfCharacters[x][0], castMember[1]]
					break
				elif castMember[0].lower() == "himself" or castMember[0].lower() == "herself":
					if fuzz.partial_token_set_ratio(pairsOfCharacters[x][1].lower(), castMember[2].lower()) > 70:
						pairsOfCharacters[x] = [pairsOfCharacters[x][0], castMember[1]]
						break
				elif fuzz.partial_token_set_ratio(pairsOfCharacters[x][1].lower(), castMember[2].lower()) > 90:
					pairsOfCharacters[x] = [pairsOfCharacters[x][0], castMember[1]]
					break

		testData.append([movieName, pairsOfCharacters])

	return testData


def bechdelTest(testData):
	"""
	Returns bechdel test results and some statistics for making the bar chart.
	:param testData: data to test. From the method above.
	:return: Results with [Movie name, True/False, mmInteractions, ffInteractions, mfInteractions, unknownInteractions]
	"""
	results = []
	test = False
	for movie in testData:
		mmInteractions = 0
		ffInteractions = 0
		mfInteractions = 0
		unknownInteractions = 0
		for pair in movie[1]:
			if pair[0] == "1" and pair[1] == "1":
				ffInteractions += 1
			elif pair[0] == "2" and pair[1] == "2":
				mmInteractions += 1
			elif pair[0] == "1" and pair[1] == "2" or pair[0] == "2" and pair[1] == "1":
				mfInteractions += 1
			else:
				unknownInteractions += 1

		if ffInteractions != 0:
			test = True

		# Some films have names different to the international standard, hence some movies may not be recognised,
		if mmInteractions + ffInteractions + mfInteractions > 100:
			results.append(
				[movie[0], str(test), mmInteractions, ffInteractions, mfInteractions, unknownInteractions])

	return results


# Call each method in secession to get test data.
films = getActionFilmNames()
filmScripts = getFilmScripts(films)
data = generateTestData(filmScripts)
bechdelTestData = bechdelTest(data)

"""
Create Bar Chart
"""
# Set Bar Width
barWidth = 0.2
bar1 = []
bar2 = []
bar3 = []
# bar4 = []
names = []
# Fill bars with data from test data.
for film in bechdelTestData:
	print(film[0] + " - Bechdel Test: " + film[1])
	bar1.append(film[2])
	bar2.append(film[3])
	bar3.append(film[4])
	# Unknown Interactions bar omitted as it is usually very big and clouds other data to be seen properly
	# bar4.append(film[5])
	names.append(film[0])

# Get values to plot the bars on the x-axis.
r1 = np.arange(len(bar1))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]
r4 = [x + barWidth for x in r3]

# make bar chart big enough so that data is visible.
plot.figure(figsize=(13, 7))
plot.subplots_adjust(left=0.1, bottom=0.5, right=0.9, top=0.9, wspace=None, hspace=None)

plot.bar(r1, bar1, color='#7f6d5f', width=barWidth, edgecolor='white', label='Male-Male Interactions')
plot.bar(r2, bar2, color='#557f2d', width=barWidth, edgecolor='white', label='Female-Female Interactions')
plot.bar(r3, bar3, color='#2d7f5e', width=barWidth, edgecolor='white', label='Male-Female Interactions')
# plot.bar(r4, bar4, color='y', width=barWidth, edgecolor='white', label='Unknown Interactions')

# Plot bar chart.
plot.xlabel('Movie', fontweight='bold')
plot.xticks([r + barWidth for r in range(len(bar1))], names, rotation='vertical')
plot.title('Number of Interactions of database recognised Movies')
plot.legend()
plot.tight_layout()

# Show Plot. If you want to save the chart, there are options to do so in the gui when the chart is opened.
plot.show()
