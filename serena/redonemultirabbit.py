from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import time

import threading

from py2neo import Graph, Node, Relationship
from ezsender.main import Rabbit 

bigdict = {} #giant dictionary for data
traveled_urls = []
traveled_count = 0
redo_rel = 0
sum_times = 0
num_urls = 0
threads = []

#recursion to collect the data

def recurse(url, depth):
	print("on url " + url)
	start_time = time.time()
	#if depth is 0 stop recursing
	if depth == 0:
		return
	#if already been here stop recursing
	if url in traveled_urls:
		global traveled_count
		traveled_count += 1
		return

	#adding urls to traveled list
	traveled_urls.append(url)
	
	#bs4 processing this url
	content = urlopen(url).read()
	soup = BeautifulSoup(content, 'html.parser')

	#finding the container for the rows with relationships
	#use regex to find all infoboxes
	bigTable = soup.find("table", {"class":re.compile("^infobox.*")})

	allLinks = [] #empty array to put all links in later
	if bigTable is not None:
		#if a table has been found, check for relationships
		allRows = bigTable.findAll("tr")
		for row in allRows:
			#for each row, check if it's a valid row
			thCheck = row.findAll("th", {"class":"infobox-label"})
			if len(thCheck) > 0:
				#it has a label and value
				tdCheck = row.find("td").findChildren("a", recursive=False)
				if len(tdCheck) > 0:
				#the value has a link
					#print("\n title is " + thCheck[0].text)
					#print("content is " + tdCheck[0].text)
					if (checkValidLink(tdCheck[0]["href"])):
						newurl = "https://en.wikipedia.org" + tdCheck[0]["href"]
						#print (newurl)
						allLinks.append(newurl[30:] + " " + thCheck[0].text)
						#continue recursion with new link
						
						
		#adding new element to dictionary
		bigdict[url[30:]] = allLinks                    
	else:
		print("No relationship table found")
	global num_urls
	num_urls += 1
	global sum_times
	print(time.time()-start_time)
	sum_times += time.time()-start_time

	for link in allLinks:
		print(link)
		threads.append(threading.Thread(target=recurse, args=("https://en.wikipedia.org/wiki/" + link.split()[0], depth-1)))
		threads[-1].start()
		#recurse("https://en.wikipedia.org/wiki/" + link.split()[0], depth-1)


def checkValidLink(url):
	invalid = [":", "=", "%", "."]
	for item in invalid:
		if item in url:
			return False
	return True
def checkNode(node_name):
	neoquery = 'match (x:Page {name:\'' + node_name + '\'}) return x'
	root_node = ( graph.evaluate(neoquery))
	if (root_node is None):
		#create new node
		root_node = Node("Page", name = node_name)
		graph.create(root_node)
	else:
		global redo_rel
		redo_rel += 1
	return root_node

"""def checkNode(node_name):
	find_node = graph.nodes.match("Page", name =node_name)
	if (len(find_node) > 0):
		global redo_rel
		redo_rel += 1
		return find_node
	else:
		root_node = Node("Page", name = node_name)
		graph.create(root_node)
		return root_node
"""

def refinery(data):
	#going to add everything in from dictionary
	for item in data:
		#for each root node
		#check if node already exists as a previous child node
		root_node = checkNode(item)
		for value in data[item]:
			#for each link stemming from the root node
			print("checking name " + value.split()[0])
			rel_node = checkNode(value.split()[0])
			graph.create(Relationship(root_node, value.split()[1], rel_node))




testNode1 = Node("Page", name = "Root")
graph = Graph(uri="bolt://localhost:7687", user="neo4j", password="demrar")
graph.delete_all()
graph.create(testNode1)

neoquery = 'match (x:Page {name:\'' + "Roosdft" + '\'}) return x'
print( graph.evaluate(neoquery))

print(len(graph.nodes.match("Pasdfs")))
print(graph.nodes.match("Pasdfsfs"))
print(len(graph.nodes.match("Page", name = "Root")))

#actual code
total_start = time.time()
depth = 3
recurse("https://en.wikipedia.org/wiki/Pope_Damasus_II", depth)
"""t1 = threading.Thread(target=recurse, args=("https://en.wikipedia.org/wiki/Pope_Damasus_II", depth))
t2 = threading.Thread(target=recurse, args=("https://en.wikipedia.org/wiki/Arthur_Blackburn", depth))
 # starting thread 1
t1.start()
# starting thread 2
t2.start()

# wait until thread 1 is completely executed
t1.join()
# wait until thread 2 is completely executed
t2.join()
"""
for thread in threads:
	thread.join()


#printing data
print(bigdict)

rab = Rabbit()
rab.connect()
rab.send_dict(bigdict)

#running refinery script
refinery(bigdict)


print("Printing metrics:")
print("Total time: " + str(time.time()-total_start))
print("Depth of " + str(depth))
print("total urls scraped: " + str(num_urls))
print("Number of duplicate pages found:" + str(traveled_count))
print("Number of times node existed already as child when adding new parent:" + str(redo_rel))
print("Average time scraping per page:" + str(sum_times/num_urls))



