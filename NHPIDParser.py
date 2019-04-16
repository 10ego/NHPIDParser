#!/usr/bin/env python
#version 0.2

import requests
from bs4 import BeautifulSoup
import json
import numpy as np

class parse():
	def __init__(self, datatype):
		base_url = "http://webprod.hc-sc.gc.ca/nhpid-bdipsn/{}Req.do?id={}&lang=eng"
		if datatype == "ingredient":
			self.URL = base_url.format("ingred", "{}")
#			self.datatype = "ing"
		elif datatype == "subingredient":
			self.URL = base_url.format("singred", "{}")
#			self.datatype = "sing"
		elif datatype == "parent_organism":
			self.URL = base_url.format("orgp", "{}")
#			self.datatype = "orgp"
		elif datatype == "organism":
			self.URL = base_url.format("org", "{}")
#			self.datatype = "org"
		elif datatype == "syn":
			self.URL = base_url.format("syn", "{}")
#			self.datatype = "syn"
	
	def _getClass(self, element):
		if "leftLabel" in element:
			return "Label"
		elif "alignedContent" in element:
			return "Content"
	def cleanValue(self, value): # list-value per key in the JSON object
		counter = 0
		opened_paranthesis = False
		for i in value:	
			counter += 1
			if i.startswith('('):
				start_paranthesis = value.index(i) - 1
				opened_paranthesis = True
			elif i.startswith(')') and opened_paranthesis is True:
				end_paranthesis = value.index(i) + 1
				joined_term = " ".join(value[start_paranthesis:end_paranthesis])
				value[start_paranthesis:end_paranthesis] = ["" for x in value[start_paranthesis:end_paranthesis]] # build empty strings to retain index size of list
				value.append(joined_term)
				opened_paranthesis = False
		value = [x for x in value if x!= "" and x!= ","] #	for deleting empty strings
		return value

	def buildHTML(self, id):
		r = requests.get(self.URL.format(str(id)))
		if r.status_code == 200:
			soup = BeautifulSoup(r.text, 'html.parser')
			joup = soup.find_all("div", class_ = ["leftLabel", "alignedContent"])
			joup = [str(element) for element in joup]
			outlist = []
			for element in joup:
				outlist.append((self._getClass(element), [text.replace("\r\n","").replace("  ","") for text in BeautifulSoup(element, 'html.parser').stripped_strings]))
			return outlist
		else:
			return "Failed to establish successful connection"

	def buildJSON(self, data):
		output = {}
		lastkey = None
		for i in data:
			## *** Check for type of data (Label vs. Content) ***
			if i[0] == "Label":
				key = i[1][0][:-1]
				if lastkey != key:
					output[key] = ""
				lasttype = "Label"
				lastkey = key
			else:
				if output[lastkey] != "":
					output[lastkey] += self.cleanValue(i[1]) 
				else:
					output[lastkey] = self.cleanValue(i[1])
		return output
		
	def fetch(self, id):
		HTML = self.buildHTML(id)
		jsonObj = self.buildJSON(HTML)
		jsonObj['id'] = str(id)
		return jsonObj