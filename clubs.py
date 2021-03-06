#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 12:30:03 2018

@author: Tyler Johnson
"""

class clubs():
	global infoList
	infoList  = {
		"None": "You have no clubs! Go to the club list to join some!",
		"Interact": "Description for Interact",
		"LEO Club": "Description for LEO Club",
		"Friends of Rachel": "Description for Friends of Rachel",
		"National Honor Society": "Description for National Honor Society",
		"Spanish Honor Society": "Description for Spanish Honor Society",
		"Math Honor Society": "Description for Math Honor Society",
		"History Honor Society": "Description for History Honor Society",
		"Student Council": "Description for Student Council",
		"Tri-M": "Description for Tri-M",
		}

	def __init__(self, name):
		global infoList
		self.name = name
		self.entries = []
		self.totalHours = 0
		if name in infoList:
			self.desc = infoList[name]
		else:
			self.desc = "Club not found."

	def __str__(self):
		return (self.name + ": " + self.desc)

	def addEntry(self, entry):
		self.entries.append(entry)
		self.totalHours += int(entry[3])

	#will return a list of all of the registered clubs as club objects
	@staticmethod
	def getAll():
		global infoList
		array = []
		for key in infoList:
			if key == "None" or key == "No Advisories":
				continue
			array.append(clubs(key))

		return array
