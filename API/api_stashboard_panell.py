import json
import requests
import unittest
import random

class api_stashboard_panell:

	base_url=""
	headers = {'content-type': 'application/json'}
	
	user="joan.arbona@uib.es"
	passwd="memCachet0"

	def __init__(self, url):
		self.base_url = url

	def preprocess(self, nomservei):
		ret=nomservei	
		ret = ret.lower()
		return ret


	def treuId(self, servei):

                append_url="/api/components"
                r = requests.get(self.base_url+append_url, auth=(self.user,self.passwd), headers=self.headers)
		try:
			for comp in json.loads(r.text)['data']:
				if servei == comp["name"]:
					return comp["id"]
		except:
			return "null"		
		return "null"		

	def ActualitzaDispositiu(self,nom,missatge,estat):

		nomservei=self.preprocess(nom)
                id=self.treuId(nomservei)
		if estat=="down":
			incident_status=1
			component_status=4
		elif estat == "up":
			incident_status=4
			component_status=1
		else:
			return -1

                data = json.dumps({"name":nomservei,"message":missatge,"status":incident_status,"component_id":id})
                append_url="/api/incidents" 
                r = requests.post(self.base_url+append_url, data=data, auth=(self.user,self.passwd), headers=self.headers)
 #               print "incident: "+r.text
    
                data = json.dumps({"id":id, "status":component_status})
                append_url="/api/components/"+str(id)
                r = requests.put(self.base_url+append_url, data=data, auth=(self.user,self.passwd), headers=self.headers)
#                print "component down: "+r.text



	def TombaServei(self, nom, missatge):
		self.ActualitzaDispositiu(nom,missatge,"down")

	def AixecaServei(self, nom, missatge):
		self.ActualitzaDispositiu(nom,missatge,"up")

	def CreaServei(self, nom, descripcio):
		
		nomservei = self.preprocess(nom)
		if self.treuId(nomservei) != "null" :
			return;
		
                data = json.dumps({"name":nomservei,"description":descripcio,"status":1})
                append_url="/api/components"
                r = requests.post(self.base_url+append_url, data=data, auth=(self.user,self.passwd), headers=self.headers)



	def getEstat(self, nom):
	#Retorna l'estat del servei: up o down.
		nomservei = self.preprocess(nom)
		id = self.treuId(nomservei)
		if id == "null":
			return "null"
		append_url="/api/components/"+str(id)
		r = requests.get(self.base_url+append_url, auth=(self.user,self.passwd), headers=self.headers)
		if json.loads(r.text)['data']['status_id'] == 1:
			return "up"
		else:
			return "down"
		


