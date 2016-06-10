#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Autor: Joan Arbona
# Script que actualitza la web de panell-estats, d'informació sobre l'estat de la infraestructura del CTI
# Es tracta d'una web que fa servir el gestor de continguts CACHET amb la qual s'hi interactua amb JSON
#

import sys
sys.path.append("/home/stashboard/panell_serveis_critics/API/")

import treu_events_grup_xml
import api_stashboard_panell #Stashboard extens
import xml.etree.ElementTree as ET

MIN_SEVERITY = 5

xml_string = treu_events_grup_xml.treu_events_grup_xml('/zport/dmd/Groups/serveis/serveis_critics')

root = ET.fromstring(xml_string)

st = api_stashboard_panell.api_stashboard_panell("http://panell-estats.sint.uib.es:80");

for disp in root.findall('dispositiu'):

	aixeca = 1 # Variable per saber si hem d'aixecar o no el servei en qüestoó

	if disp.text != "udp.sint.uib.ess":
		st.CreaServei(disp.text, "Dispositiu Servei Critic")

		if len(disp) > 0:
			for event in disp.findall('event'):
				message = event.find('message')
				severity = event.find('severity')
				device_groups_str = ET.tostring(event)
				##########################################################
				#Cal mirar si el device de l'event es critic, 
				#ja que de vegades se'ns en colen: En fer
				#getEvent, apareixen events d'altres dispositius. 
				#Per exemple, en voler treure els events de rrhh apareixen també 
				#els events de rrhh.db.uib.es
				##########################################################
				if device_groups_str.find("serveis_critics") > -1 and int(severity.text) >= MIN_SEVERITY:
				##########################################################
				#Si l'event és de serveis crítics i la severitat de l'event és suficient tombam el servei
				#Sino, ignoram l'event.
				##########################################################
				#	print disp.text+" tomba"
					aixeca = 0
			

		##########################################################
		# Miram si el dispositiu ja no té events, però també cal mirar 
		#la severitat d'aquests events! Si no cumpleix el mínim de severitat
		# per tal de ser tombat l'aixecam.
		##########################################################
		if aixeca == 1:
			if st.getEstat(disp.text) == "down":
				st.AixecaServei(disp.text,"El servei funciona correctament.")
	#			sm_st.AixecaServei(disp.text)
		else:
			if st.getEstat(disp.text) == "up":
				st.TombaServei(disp.text,"Sembla que el servei està experimentant alguns problemes. Estam treballant perquè torni a estar operatiu el més aviat possible.")
	#			sm_st.TombaServei(disp.text)
