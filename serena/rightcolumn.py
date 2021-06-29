from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

from py2neo import Graph, Node, Relationship



def recurse(previousNode, url, depth):
    print("\n New url is " + url)

    if depth == 0:
        return
    content = urlopen(url).read()
    soup = BeautifulSoup(content, 'html.parser')
    bigTable = soup.find("table", {"class":"infobox vcard"})
    if bigTable == None:
        bigTable = soup.find("table", {"class":"infobox"})
    #print(bigTable.prettify())

    if bigTable is not None:
        allRows = bigTable.findAll("tr")
        print(allRows)

        for row in allRows:
            #check if it's a valid row
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
                        newNode = Node("Page", name = tdCheck[0].text)
                        graph.create(newNode)
                        graph.create(Relationship(previousNode, thCheck[0].text, newNode))
                        recurse(newNode, newurl, depth-1)

    else:
        print("i can't find big table")
        return
#actual program



testNode1 = Node("Page", name = "Root")
graph = Graph(uri="bolt://localhost:11007", user="neo4j", password="demrar")
graph.delete_all()
graph.create(testNode1)
recurse(testNode1, "https://en.wikipedia.org/wiki/Pope_Francis", 3)
