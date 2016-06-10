import json
import requests
import unittest
import random

class api_stashboard_panell:

	VER=False
	base_url=""
	headers = {'content-type': 'application/json', 'X-Cachet-Token':'TGUTJqjJ6GXlTndt27hP'}
	
	
	user="joan.arbona@uib.es"
	passwd="memCachet0"

	def __init__(self, url, token):
		self.base_url = url
		self.headers = {'content-type': 'application/json', 'X-Cachet-Token' :token}

	def preprocess(self, nomservei):
		ret=nomservei	
#		ret = ret.lower()
		return ret


	def treuId(self, servei, grup=False):

		if grup == False :
	                append_url="/api/v1/components"
		elif grup == True :
	                append_url="/api/v1/components/groups"

                r = requests.get(self.base_url+append_url, headers=self.headers, verify=self.VER)
		try:
			while r != None:
				for comp in json.loads(r.text)['data']:
					if servei == comp["name"]:
						return comp["id"]
				r = requests.get(json.loads(r.text)['meta']['pagination']['links']['next_page'], headers=self.headers, verify=self.VER)
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
		elif estat == "perf":
		#perf issues
			incident_status=1
			component_status=2
		else:
			return -1

                data = json.dumps({"name":nomservei,"message":missatge,"status":incident_status,"component_id":id})
                append_url="/api/v1/incidents" 
                r = requests.post(self.base_url+append_url, data=data, headers=self.headers, verify=self.VER)
 #               print "incident: "+r.text
    
                data = json.dumps({"id":id, "status":component_status})
                append_url="/api/v1/components/"+str(id)
                r = requests.put(self.base_url+append_url, data=data, headers=self.headers, verify=self.VER)
#                print "component down: "+r.text



	def TombaServei(self, nom, missatge):
		self.ActualitzaDispositiu(nom,missatge,"down")

	def AixecaServei(self, nom, missatge):
		self.ActualitzaDispositiu(nom,missatge,"up")

	def ReportaServei(self, nom, missatge):
		self.ActualitzaDispositiu(nom,missatge,"perf")

	

	def CreaServei(self, nom, descripcio):
	#Crea el servei o l'actualitza si ja existeix		
	# Retorna Id del component
		nomservei = self.preprocess(nom)
		idservei=self.treuId(nomservei)
		if idservei != "null" :
		# Si ja existeix el servei actualitzam i tornam
			self.setDescComponent(idservei,descripcio) # Actualitzam descripcio
			return idservei

		else:
		# Si no existeix el servei el cream
			data = json.dumps({"name":nomservei,"description":descripcio,"status":1})
	                append_url="/api/v1/components"
        	        r = requests.post(self.base_url+append_url, data=data,  headers=self.headers, verify=self.VER)
			return json.loads(r.text)["data"]["id"]

	def ActualitzaGrup(self, nom, grup):
	# Actualtiza el grup dun servei. Si grup=="null" el borra.
		if grup == "":
			return "null"

                nomservei = self.preprocess(nom)
                idservei=self.treuId(nomservei)
                if idservei == "null" :
			raise Exception("El servei no existeix")
			return "null"
		else:
			if grup != "null" :
				self.setGrup(idservei,grup)
			else:
                                self.delGrup(idservei)
			return idservei


	def CreaGrup(self, grup):
	# Crea el grup. Si ja existeix retorna el seu ID
		gr_id=self.treuId(grup, grup=True);
                if gr_id  == "null" :
                        # Si el grup no existeix
                        data = json.dumps({"name":grup, "collapsed":"1"})
                        append_url="/api/v1/components/groups"
                        r  = requests.post(self.base_url+append_url, data=data,  headers=self.headers, verify=self.VER)
                        gr_id=json.loads(r.text)["data"]["id"]
		return gr_id
			
	def setGrup(self, id, grup):
	# Set grup dispositiu
		gr_id = self.CreaGrup(grup)
                data = json.dumps({"id":id, "group_id":gr_id, "status":self.getStatusFromId(id)})
                append_url="/api/v1/components/"+str(id)
	        r = requests.put(self.base_url+append_url, data=data, headers=self.headers, verify=self.VER)		
			
	def delGrup(self, id):
	# Elimina el grup del component
                data = json.dumps({"id":id, "group_id":0, "status":self.getStatusFromId(id)})
                append_url="/api/v1/components/"+str(id)
	        r = requests.put(self.base_url+append_url, data=data, headers=self.headers, verify=self.VER)		


	def getGrup(self, id):
	# Get grup dispositiu
                append_url="/api/v1/components/"+str(id)
                r = requests.get(self.base_url+append_url,  headers=self.headers, verify=self.VER)
                gr_id=json.loads(r.text)['data']['group_id']
                append_url="/api/v1/components/groups/"+str(gr_id)
		try:
			r = requests.get(self.base_url+append_url,  headers=self.headers, verify=self.VER)
			return json.loads(r.text)['data']['name']
		except:
			print "Component "+str(id)+" no te grup"
			return "null";

	def getNomComponent(self,id):
                append_url="/api/v1/components/"+str(id)
                r = requests.get(self.base_url+append_url,  headers=self.headers, verify=self.VER)
		return json.loads(r.text)['data']['name']


	def setNomComponent(self,id,nom):
        # Set nom dispositiu
                data = json.dumps({"id":id, "name":nom, "status":self.getStatusFromId(id)})
                append_url="/api/v1/components/"+str(id)
                r = requests.put(self.base_url+append_url, data=data, headers=self.headers, verify=self.VER)


	def getDescComponent(self,id):
                append_url="/api/v1/components/"+str(id)
                r = requests.get(self.base_url+append_url,  headers=self.headers, verify=self.VER)
		return json.loads(r.text)['data']['description']
		
	def setDescComponent(self,id,desc):
                data = json.dumps({"id":id, "description":desc, "status":self.getStatusFromId(id)})
                append_url="/api/v1/components/"+str(id)
                r = requests.put(self.base_url+append_url, data=data, headers=self.headers, verify=self.VER)

	def getEstat(self, nom):
	#Retorna l'estat del servei: up o down.
		nomservei = self.preprocess(nom)
		id = self.treuId(nomservei)
		if id == "null":
			return "null"
		append_url="/api/v1/components/"+str(id)
		r = requests.get(self.base_url+append_url,  headers=self.headers, verify=self.VER)
		if json.loads(r.text)['data']['status'] == 1:
			return "up"
		elif  json.loads(r.text)['data']['status'] == 2:
			return "perf"
		else:
			return "down"
		

	def getEstatId(self, id):
	#Retorna l'estat del servei: up o down.
		append_url="/api/v1/components/"+str(id)
		r = requests.get(self.base_url+append_url,  headers=self.headers, verify=self.VER)
		if json.loads(r.text)['data']['status'] == 1:
			return "up"
		elif  json.loads(r.text)['data']['status'] == 2:
			return "perf"
		else:
			return "down"

	def getStatusFromId(self, id):
	#Retorna l'estat del servei: up o down.
		append_url="/api/v1/components/"+str(id)
		r = requests.get(self.base_url+append_url,  headers=self.headers, verify=self.VER)
		return json.loads(r.text)['data']['status']

	def eliminaServei(self, id):
	#Retorna l'estat del servei: up o down.
		append_url="/api/v1/components/"+str(id)
		r = requests.delete(self.base_url+append_url,  headers=self.headers, verify=self.VER)

	def eliminaGrups(self, id):
	#Retorna l'estat del servei: up o down.
		append_url="/api/v1/components/groups/"+str(id)
		r = requests.delete(self.base_url+append_url,  headers=self.headers, verify=self.VER)

	def eliminaIncident(self, id):
	#Retorna l'estat del servei: up o down.
		append_url="/api/v1/incidents/"+str(id)
		r = requests.delete(self.base_url+append_url,  headers=self.headers, verify=self.VER)
