#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Autor: Joan Arbona
# Script de proves per actualitzar el panell d'estats simple.
# Basicament es tracta d'un script que actualitza un servidor Web amb JSON
#

import sys
sys.path.append("/home/stashboard/panell_serveis_critics/API/")

import treu_events_grup_xml
import api_stashboard_web #Stashboard django
import xml.etree.ElementTree as ET

####################################
# Estructura de dades que guarda la relació URL - Nom del servei
####################################
llista_serveis = {

	"uibdigital.uib.es":"UIBDigital",
	"www.uib.es":"Pàgina Web",
	"ox.uib.es":"Correu",
	"smtp.uib.es":"Correu",
	"print.uib.es":"Servei d'impressió",
	"wiki.uib.es":"Wiki",
	"jira.uib.es":"Jira",
	"wwws.fueib.es":"Fueib",
	"udp.sint.uib.es":"Test"
}


MIN_SEVERITY = 4

xml_string = treu_events_grup_xml.treu_events_grup_xml('/zport/dmd/Groups/serveis/serveis_critics')
# Podem mostrar l'arbre XML amb print xml_string

root = ET.fromstring(xml_string)

sm_st = api_stashboard_web.api_stashboard_web("https://panell-estats.sint.uib.es");

for disp in root.findall('dispositiu'):

	max_severitat = 0 # Emmagatzema la severitat màxima trobada en un dispositiu
	if disp.text != "udp.sint.uib.ef": # udp.sint només està per fer proves.
		if disp.text in llista_serveis: # Si cal, cream el servei
			sm_st.CreaServei(llista_serveis[disp.text])

	if len(disp) > 0: # Iteram entre tots els dispositius
		for event in disp.findall('event'): # I llurs events...
			message = event.find('message')
			severity = event.find('severity')
			device_groups_str = ET.tostring(event)
			##########################################################
			# La comprovació de que el dispositiu sigui de serveis crítics ve pel següent:
			# Cal mirar si el device de l'event es critic, 
			# ja que de vegades se'ns en colen: En fer
			# getEvent, apareixen events d'altres dispositius. 
			# Per exemple, en voler treure els events de rrhh apareixen també 
			# els events de rrhh.db.uib.es. Els caràcters de final d'string semblen no funcionar.
			##########################################################
			if device_groups_str.find("serveis_critics") > -1 and int(severity.text) >= MIN_SEVERITY:
			##########################################################
			# Cercam el màxim valor de severitat que tenen els events d'aquest dispositiu i el 
			# guardam a max_severitat
			##########################################################
				if max_severitat < int(severity.text):
					max_severitat = int(severity.text)
	
	##########################################################################
	# Actualitzam l'estat del dispositiu amb el màxim valor de severitat que li hem trobat, sempre 
	# i quan estigui dins la llista de serveis que hem especificat a l'script 
	# Per no fer operacions inútils, comprovam abans que l'estat hagi canviat.
	##########################################################################
	if disp.text in llista_serveis and sm_st.getEstat(llista_serveis[disp.text]) != max_severitat:
		sm_st.ActualitzaDispositiu(llista_serveis[disp.text], max_severitat)
