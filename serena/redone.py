from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

from py2neo import Graph, Node, Relationship

bigdict = {} #giant dictionary for data
traveled_urls = []
traveled_count = 0
redo_rel = 0

#recursion to collect the data
def recurse(url, depth):

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
					print("\n title is " + thCheck[0].text)
					print("content is " + tdCheck[0].text)
					if (":" not in tdCheck[0]["href"][6:] and "=" not in tdCheck[0]["href"][6:] and "%" not in tdCheck[0]["href"][6:]):
						newurl = "https://en.wikipedia.org" + tdCheck[0]["href"]
						print (newurl)
						allLinks.append(newurl[30:] + " " + thCheck[0].text)
						#continue recursion with new link
						recurse(newurl, depth-1)
		#adding new element to dictionary
		bigdict[url[30:]] = allLinks                    
	else:
		print("No relationship table found")

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
recurse("https://en.wikipedia.org/wiki/Pope_Damasus_II", 3)

#printing data
print(bigdict)

#running refinery script
refinery(bigdict)

print(traveled_count)
print(redo_rel)



