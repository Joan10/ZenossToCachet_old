#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Autor: Joan Arbona
# Script que actualitza la web de panell-estats, d'informació sobre l'estat de la infraestructura del CTI
# Es tracta d'una web que fa servir el gestor de continguts CACHET amb la qual s'hi interactua amb JSON
#

import sys
sys.path.append("/home/stashboard/panell_serveis_critics_v2/API/")

import treu_events_grup_xml
import api_stashboard_panell_v2 #Stashboard extens
import xml.etree.ElementTree as ET
import ZenossAPI

MIN_SEVERITY = 5

xml_string = treu_events_grup_xml.treu_events_grup_xml('/zport/dmd/Groups/serveis/serveis_critics')

root = ET.fromstring(xml_string)

st = api_stashboard_panell_v2.api_stashboard_panell("http://panell-estats-cti.sint.uib.es:8080","TGUTJqjJ6GXlTndt27hP");# Exclusiu del CTI 
st2 = api_stashboard_panell_v2.api_stashboard_panell("http://panell-estats.sint.uib.es:8080","HISEU50ehqdi86Imehlw");# Public
zp=ZenossAPI.ZenossAPI()

def actualitza(st, id, nom, perfok, aixeca):
	if aixeca == 1:
        	if perfok == 0:
                	if st.getEstatId(id) != "perf":
                        	st.ReportaServei(nom, "El servei està experimentant problemes de rendiment.")
                else:
                        if st.getEstatId(id) != "up":
                                st.AixecaServei(nom,"El servei funciona correctament.")
        else:
               if st.getEstatId(id) != "down":
			st.TombaServei(nom,"Sembla que el servei està experimentant alguns problemes. Estam treballant perquè torni a estar operatiu el més aviat possible.")

for disp in root.findall('dispositiu'):

	aixeca = 1 # Variable per saber si hem d'aixecar o no el servei en qüestoó
	perfok = 1 # Variable per saber si el servei té un rendiment correcte
	if disp.text != "udp.sint.uib.es":
		try:
			# Parsejam el nom del dispositiu. Aquest anirà contingut dins el camp Comments del Zenoss de la forma següent:
			# cachet=<nom>;
			# Si no el troba posarà el nom del Device del Zenoss
			comentari=zp.get_devicecomment(zp.get_UID(disp.text))
			offset0=comentari.find("cachet=");
			offset1=comentari.find(";");
			if offset0 > -1 and offset1 > -1:
				nom=comentari[offset0+7:offset1]
			else:
				raise Exception("Comentari al Zenoss mal format. El nom va contingut dins cachet=<nom>;")
			
                        offset2=comentari.find("public=");
                        offset3=comentari.find(";",offset2+1)
                        if offset2 > -1 and offset3 > -1: # Treim el nom public del servei
                                nompublic=comentari[offset2+7:offset3]
                        else:
                                nompublic="null"

		except:
                        nompublic="null"
			nom=disp.text
#
		# No actualitzam el grup, finalment ho feim manualment.
		id=st.CreaServei(nom, "Dispositiu "+disp.text)
                if nompublic != "null":
                        id2=st2.CreaServei(nompublic, "") # Es crea el servei només si s'ha especificat nom public

		if len(disp) > 0:
			for event in disp.findall('event'):
				message = event.find('message')
				severity = event.find('severity')
				count = event.find('count')
				device_groups_str = ET.tostring(event)
				##########################################################
				#Cal mirar si el device de l'event es critic, 
				#ja que de vegades se'ns en colen: En fer
				#getEvent, apareixen events d'altres dispositius. 
				#Per exemple, en voler treure els events de rrhh apareixen també 
				#els events de rrhh.db.uib.es
				##########################################################
				try:
					if device_groups_str.find("serveis_critics") > -1:
						if int(severity.text) >= MIN_SEVERITY:
						##########################################################
						#Si l'event és de serveis crítics i la severitat de l'event és suficient tombam el servei
						#Sino, ignoram l'event.
						##########################################################
						#	print disp.text+" tomba"
							aixeca = 0
						##########################################################
						#Si l'event no és crític, però té problemes de rendiment, ho reflexam a la pàgina.
						##########################################################
						elif message.text.find("threshold of") > -1 and int(count.text) > 2:
							perfok = 0	
				except:
					print "Ooops. Error en un event de "+nom
					pass
					

		##########################################################
		# Miram si el dispositiu ja no té events, però també cal mirar 
		#la severitat d'aquests events! Si no cumpleix el mínim de severitat
		# per tal de ser tombat l'aixecam.
		##########################################################

		actualitza(st,id,nom,perfok,aixeca)
		if nompublic != "null": # Si te nom públic l'actualitzam també a st2
			actualitza(st2,id2,nompublic,perfok,aixeca)

