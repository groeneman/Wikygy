import urllib
import extMainText
import tfidf
import calais
import sphinx_inter
from sphinx_vars import *
from operator import itemgetter
from itertools import chain

calaisAPI = "pqwxutrgjk8zhk5geutnhpyj"
cc = calais.Calais(calaisAPI)
t = tfidf.TfIdf(corpus_filename="/Accounts/groenemm/summer/wikygy/wikilink/etc/data/reformattedfreqlist.txt",\
				stopword_filename="/Accounts/groenemm/summer/wikygy/wikilink/etc/data/stopwords.txt")
sc = sphinx_inter.SphinxClient("dmusican41812",rankingmode=SPH_RANK_BM25,fieldweights={"title":4, "body":1})

def getText(url):
	page = urllib.urlopen(url).read()
	page = unicode(page, "utf-8")
	text = extMainText(page).strip()
	return text

def removeSphinxReservedChars(word):
	word= word.lstrip("!@^-*'")
	word = word.rstrip("$'")
	return word

def getTextFromURL(url):
	try:
		text = getText(url)
	except IOError,e:
		print e
		return None
	except UnicodeDecodeError,e:
		print e
		return None
	else:
		return text

def getCalaisTags(url,limit=10):
	global cc

	result = cc.analyze_url(url)
	topics = getTopics(result)
	topics.sort(reverse=True,key=itemgetter(2))
	return topics[:limit]

def reformMultiwordTopic(t):
	words = t.split(" ")
	if len(words)>1:
		#return "\"" + t + "\""
		return " | ".join(words)
	else:
		return t

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

def getCalaisQuery(text,url=None,numresults=10):
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
	else:
		titles = results.getMatchesByAttr("title")[:numresults]
		ids = results.getMatchIDs()[:numresults]
	return zip(titles,ids)

def getWikiLinks(text,numresults=10):
	q1 = getTFIDFQuery(text)
	results = runQuery(q1,numresults)
	return results
	
