# -*- coding: utf-8 -*-
import json
import requests
import unittest
import random

class api_stashboard_web:


	base_url=""
	headers = {'content-type': 'application/json; charset=utf8'}
	
	user="jdeu"
	passwd="cti1305"

	def __init__(self, url):
		self.base_url = url

	def preprocess(self, nomservei):
		ret=nomservei
		return ret

	def treuId(self, servei0):

                append_url="/serveis/"
		servei=self.preprocess(servei0)
                r = requests.get(self.base_url+append_url, auth=(self.user,self.passwd), headers=self.headers, verify=False)
		r.encoding = 'utf-8' #Si no s'especifica dóna problemes
		try:
			for comp in json.loads(r.text):
				if servei.decode('utf-8') == comp["nom"]:
					return comp["id"]
		except:
			return "null"
		return "null"	

	def ActualitzaDispositiu(self,nom,estat):

		nomservei=self.preprocess(nom)
		id=self.treuId(nomservei)
  #              data = json.dumps({"name":nomservei,"message":missatge,"status":incident_status,"component_id":id})
 #               append_url="/serveis/"+nom 
#                r = requests.post(self.base_url+append_url, data=data, auth=(self.user,self.passwd), headers=self.headers)
 #               print "incident: "+r.text
                data = json.dumps({"nom":nomservei, "estat":estat})
                append_url="/serveis/"+str(id)+"/"
                r = requests.put(self.base_url+append_url, data=data, auth=(self.user,self.passwd), headers=self.headers, verify=False)
#                print "component down: "+r.text

	def CreaServei(self, nom):
		
		nomservei = self.preprocess(nom)
		if self.getEstat(nomservei) != "null" :
			return -1

                data = json.dumps({"nom":nomservei, "estat":0})
                append_url="/serveis/"
                r = requests.post(self.base_url+append_url, data=data, auth=(self.user,self.passwd), headers=self.headers,verify=False)

	def EsborraServei(self, nom):
		nomservei = self.preprocess(nom)
                id=self.treuId(nomservei)
	
                append_url="/serveis/"+str(id)+"/"
                r = requests.delete(self.base_url+append_url, auth=(self.user,self.passwd), headers=self.headers,verify=False)


	def getEstat(self, nom):
	#Retorna l'estat del servei
#Estats zenoss: 
#		0 OK
#		1,2 INFO
#		3 WARN
#		4 ERROR
#		5 CRIT

		nomservei = self.preprocess(nom)
                id=self.treuId(nomservei)
		if id == "null":
			return "null"

		append_url="/serveis/"+str(id)+"/"

		r = requests.get(self.base_url+append_url, auth=(self.user,self.passwd), headers=self.headers,verify=False)
		data = json.loads(r.text)
		try:
			return data["estat"]
		except:
			return "error"

