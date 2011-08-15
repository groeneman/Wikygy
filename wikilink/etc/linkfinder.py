import urllib
from extMainText import extMainText
import tfidf
import calais
import sphinx_inter
from sphinx_vars import *
from operator import itemgetter
from itertools import chain
import re

calaisAPI = "pqwxutrgjk8zhk5geutnhpyj"
cc = calais.Calais(calaisAPI)
t = tfidf.TfIdf(corpus_filename="/Accounts/groenemm/summer/wikygy/wikilink/etc/data/reformattedfreqlist.txt",\
				stopword_filename="/Accounts/groenemm/summer/wikygy/wikilink/etc/data/stopwords.txt")
sc = sphinx_inter.SphinxClient("dmusican41812",rankingmode=SPH_RANK_BM25,fieldweights={"title":4, "body":1})

def getText(pageText):
	pageText = unicode(pageText, "utf-8")
	text = extMainText(pageText).strip()
	return text

def removeSphinxReservedChars(word):
	word= word.lstrip("!@^-*'")
	word = word.rstrip("$'")
	return word

def getTextFromURL(url):
	try:
		title,text = getTextAndTitleFromURL(url)
	except IOError,e:
		print e
		return None,None
	except UnicodeDecodeError,e:
		print e
		return None,None
	else:
		return title,text

def getTextAndTitleFromURL(url):
	page = urllib.urlopen(url).read()
	text = getText(page)
	title = re.findall("<title>(.*)</title>",page)
	if len(title) > 0:
		title = title[0]
	else:
		title = None
	return title,text

def getTopics(resultobj):
	if hasattr(resultobj, "entities"):
		return [(item['_type'], item['name'], item['relevance']) for item in resultobj.entities]
	else:
		return []

def getCalaisTags(url,limit=10):
	global cc

	result = cc.analyze_url(url)
	topics = getTopics(result)
	topics.sort(reverse=True,key=itemgetter(2))
	return topics[:limit]

def tagsToQueryString(taglist):
	global t

	taglist = [tag[1].strip().split() for tag in taglist]
	taglist = chain.from_iterable(taglist)
	taglist = t.remove_stopwords(taglist)
	taglist = [tag for tag in taglist if len(tag) > 1]
	query = " | ".join(set(taglist))
	return query


def cleanText(wordList):
	global t
	wordList = [removeSphinxReservedChars(word) for word in wordList]
	wordList = [word for word in wordList if not word.isdigit() and len(word)>1]
	wordList = t.remove_stopwords(wordList)
	return wordList

def getTFIDFQuery(text,url=None,numwords=10):
	global t
	words = t.get_doc_keywords(text)
	words = [word[0] for word in words]
	words = cleanText(words)[:numwords]
	return " | ".join(set(words))

def getFirstNWordsQuery(text,url=None,numwords=100):
	global t
	words = t.get_tokens(text)[:numwords]
	words = cleanText(words)
	return " | ".join(words)

def getCalaisQuery(url,numresults=10):
	assert url is not None
	global t
	tags = getCalaisTags(url)
	return tagsToQueryString(tags)

def runQuery(query,numresults=10,verbose=False):
	global sc
	error = False
	rank = None

	try:
		results = sc.query(query)
	except sphinx_inter.SphinxAPIException,e:
		print "Error: {0}".format(e)
		error = True
		return []
	else:
		return results.getResults("title")

def getWikiLinks(url,text=None,numresults=10):
	
	q1 = getTFIDFQuery(text)
	results1 = runQuery(q1,numresults)
	
	try:
		q2 = getCalaisQuery(url)
	except ValueError:
		results2 = []
	else:
		results2 = runQuery(q2,numresults)
	

	print "**************"
	print "TFIDF: ",q1
	#print "Calais: ",q2
	print "URL: ",url
	print "Extracted Text: ", text
	
	results = []
	
	while len(results)< numresults:
		if (len(results) %2 == 0 or len(results2) ==0) and len(results1)>0:
			results.append(results1.pop(0))
		elif (len(results) %2 == 1 or len(results1) == 0) and len(results2)>0:
			results.append(results2.pop(0))
		else:
			#Nothing left to add
			break
	
	return results
	
