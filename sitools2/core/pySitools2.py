# -*- coding: utf-8 -*-

#    SITools2 client for Python
#    Copyright (C) 2013 - Institut d'astrophysique spatiale
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This is a generic python Sitools2 tool
pySitools2 tool has been designed to perform all operations available within Sitools2.
The code defines several classes SitoolsInstance, Field, Query, Dataset and Project. 
Example of application : 
A Solar tool to request and retrieve SDO data from IAS (Institut d'Astrophysique Spatiale)
see http://sdo.ias.u-psud.fr/python/sdo_client_idoc.html



@author: Pablo ALINGERY for IAS 28-08-2012
"""
__version__ = "1.0"
__license__ = "GPLV3"
__author__ ="Pablo ALINGERY"
__credit__=["Pablo ALINGERY", "Elie SOUBRIE"]
__maintainer__="Pablo ALINGERY"
__email__="pablo.alingery.ias.u-psud.fr, pablo.alingery@exelisvis.com"


import sys
import logging
from datetime import *

try :
	import urllib
except:
        messageError = "Import failed in module pySitools2_idoc :\n\turllib module is required\n"
	sys.stderr.write(messageError)
	raise ImportError(messageError)
try :
	import simplejson
except:
        messageError = "Import failed in module pySitools2_idoc :\n\tsimplejson module is required\n"
	sys.stderr.write(messageError)
	raise ImportError(messageError)
try :
	from xml.dom.minidom import parseString
except:
        messageError = "Import failed in module pySitools2_idoc :\n\txml.dom.minidom module is required\n"
	sys.stderr.write(messageError)
	raise ImportError(messageError)

class Sitools2Exception(Exception):
    """SITools2 Exception"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class _Log(object):
    """Module Logger.
    Create a module logger with the following format '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    """    
    @staticmethod
    def getLogger(name, level = logging.INFO):
        """Returns the logger
        
        Parameters
        ----------
            name : logger name
            level : logging.level (par default logging.INFO)
        
        """
        # create logger
        logger = logging.getLogger(name) 
        logger.setLevel(level)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(level)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(ch)
        return logger        
    
    
class Sitools2Instance:
    """"Class to retrieve the list of project.
	An instance of Sitools2Instance is defined using its url.
	The method available : list_project(). 
	It will return a list of the projects available for the instance.
    """        

    def __init__(self, url):
        """Constructs a SITools2Instance with an url and a log level."""
	self.instanceUrl=url
        self.__logger = _Log.getLogger(self.__class__.__name__) 
	try :
                self.__logger.debug(urllib.unquote((url+"/sitools/portal").encode('ascii')).decode('utf-8'))
		simplejson.load(urllib.urlopen(url+"/sitools/portal"))
	except:
		err_mess="Sitools2 instance %s not available please contact admin for more info\n" % url
                self.__logger.error(err_mess)		
		raise Sitools2Exception(err_mess)        
            

    def list_project(self, **kwargs):
        """Returns the list of projects available for the SITools2 instance."""
	sitools_url=self.instanceUrl
	data=[]
	kwargs.update({
		'media' : 'json'
	})
	url=sitools_url+'/sitools/portal/projects'+'?'+urllib.urlencode(kwargs)
        self.__logger.debug(urllib.unquote(url.encode('ascii')).decode('utf-8'))
	result =simplejson.load(urllib.urlopen(url))
	out_mess= "%s projects detected\n" % result['total']
        self.__logger.info(out_mess)
	projects=result['data']
	for i,project in enumerate(projects) :
		p_url=sitools_url+project['sitoolsAttachementForUsers']		
		try :
			data.append(Project(p_url))
		except :
			out_mess="Cannot create object project %s, %s protected \nContact admin for more info\n" % (project['name'],p_url)
                        self.__logger.error(out_mess)			
			raise Sitools2Exception(out_mess)
	return data

class Field:
    """Definition of a Field class.
       A field is a item from a dataset. 
       It has several attributes : name, type, filter(boolean), sort(boolean), behavior.
    """
    
    def __init__(self,dictionary):
        """Constructor with a dictionary"""
	self.name=""
	self.type=""
	self.filter=False
	self.sort=False
	self.behavior=""
	self.__compute_attributes(dictionary)

    def __compute_attributes(self, dictionary):
        """Compute attributes from web service dataset description."""
	if dictionary.has_key('columnAlias'):
		self.name=dictionary['columnAlias']
	if dictionary.has_key('sqlColumnType'):	
		self.type=dictionary['sqlColumnType']
	if dictionary.has_key('filter'):	
		self.filter=dictionary['filter']
	if dictionary.has_key('sortable'):	
		self.sort=dictionary['sortable']
	if dictionary.has_key('columnRenderer'):
		self.behavior=dictionary['columnRenderer']['behavior']
    
    def get_name(self):
        """Returns the name."""
        return self.name
    
    def get_type(self):
        """Returns the type."""
        return self.type
    
    def get_filter(self):
        """Returns the filter."""
        return self.filter
    
    def get_sort(self):
        """Returns the sort."""
        return self.sort
    
    def get_behavior(self):
        """Returns the behavior."""
        return self.behavior
    
    def __display_variable(self, name):
        """Returns name if the name != None otherwise \"\""""
        if name == None:
            return ""
        else:
            return name
    
    def display(self):
        """Ouptut attributes of Field."""
	print self.__repr__()

    def __repr__(self):
	return ("Field object display() :\n\t%s\n\t\ttype : %s\n\t\tfilter : %s\n\t\tsort : %s\n\t\tbehavior : %s" %(self.__display_variable(self.name),self.__display_variable(self.type),self.filter,self.sort, self.__display_variable(self.behavior)))


class Query():
    """Definition of a Query class.
       A Query defines the request passed to the server. 
       It can have the following attributes : fields_list, name_list, operation.
       The parameter operation can value : ge, le, gte, lte, lt, eq, gt, lte, like, in, numeric_between, date_between, cadence (dev for IAS) .
    """

    def __init__(self, param_list):
        """Constructor."""
	self.fields_list=[]
	self.name_list=[]
	self.value_list=[]
	self.operation=""
        self.__logger = _Log.getLogger(self.__class__.__name__) 
	self.__compute_attributes(param_list)

    def __compute_attributes(self,param_list) :
        """Compute attribute from client request."""
	if type(param_list[0]).__name__ !='list':
		mess_err="Query first argument type is : %s\nQuery first argument type should be : list\n" % type(param_list[0]).__name__
                self.__logger.error(mess_err)		
		raise Sitools2Exception(mess_err)
	if type(param_list[1]).__name__ !='list':
		mess_err="Query second argument type is : %s\nQuery second argument type should be : list\n\n\n" % type(param_list[1]).__name__
                self.__logger.error(mess_err)		
		raise Sitools2Exception(mess_err)
	for field in param_list[0]:
		self.name_list.append(field.name)
	self.fields_list=param_list[0]
	self.value_list=param_list[1]
	self.operation=param_list[2]

    def get_fields(self):
        return self.fields_list
    
    def get_names(self):
        return self.name_list
    
    def get_values(self):
        return self.value_list
    
    def get_operation(self):
        return self.operation

    def __display_variable(self, name):
        """Returns name if the name != None otherwise \"\""""
        if name == None:
            return ""
        else:
            return name
        
#Ouptut attributes of Query
    def display(self):
	print self.__repr__()

#Define a repr of this Class 
    def __repr__(self):
	return ("name : % s\nvalue : %s\nOperation : %s" % (", ".join(self.name_list), ", ".join(self.value_list), __display_variable(self.operation)))



class Dataset:
    """Definition of a Dataset class.
       It is related to a Sitools2 dataset, which is a set of instances of the class Field with specific properties.
       It can have the following attibutes  : name, description, url, field_list,filter_list, resources_target, noClientAccess_list, primary_key,resources_list.  
       Dataset provides the generic powerfull search method that allows a python client to make a request on a Sitools2 installation.
    """        
#Initialize class Dataset
    def __init__(self, url):
        self.__logger = _Log.getLogger(self.__class__.__name__)
	try :
		simplejson.load(urllib.urlopen(url))
	except:
		err_mess="Dataset %s not available, please contact admin for more info\n" % url	
                self.__logger.error(err_mess)
		raise Sitools2Exception(err_mess)
        self.name = ""
        self.description = ""
	self.uri="/"+url.split("/")[-1]
        self.url = url
	self.fields_list=[]
	self.fields_dict={}
	self.filter_list=[]
	self.allowed_filter_list=[]
	self.sort_list=[]
	self.allowed_sort_list=[]
	self.resources_target=[]
	self.noClientAccess_list=[]
	self.primary_key=""
	self.__compute_attributes()
	self.resources_list()
#Compute attribute from web service answer dataset description
    def __compute_attributes(self, **kwargs) :
	kwargs.update({
		'media' : 'json'
	})
	url=self.url+'?'+urllib.urlencode(kwargs)
        self.__logger.debug(urllib.unquote(url.encode('ascii')).decode('utf-8'))
	try:
		result =simplejson.load(urllib.urlopen(url))
		self.name=result['dataset']['name']
		self.description=result['dataset']['description']
		columns=result['dataset']['columnModel']
		for column in columns :
			self.fields_list.append(Field(column))
			self.fields_dict.update({
				column['columnAlias'] : Field(column)
			})
			if (column.has_key('filter') and column['filter']):
				self.filter_list.append(Field(column))
			if (column.has_key('sortable') and column['sortable']):
				self.sort_list.append(Field(column))
			if (column.has_key('primaryKey') and column['primaryKey']):
				self.primary_key=(Field(column))
			if (column.has_key('columnRenderer')and column['columnRenderer']['behavior']=="noClientAccess"):
				self.noClientAccess_list.append(column['columnAlias'])
	except :
		err_mess="Error in Dataset.compute_attributes(), please contact admin  for more info"
                self.__logger(err_mess)		
		raise Sitools2Exception(err_mess)
	for field in self.filter_list:
		self.allowed_filter_list.append(field.name)
	for field in self.sort_list:
		self.allowed_sort_list.append(field.name)
#Explore and list dataset resources (method=options has to be allowed )
    def resources_list(self):
	try :
		url = urllib.urlopen(self.url+'?method=OPTIONS') 
        	wadl = url.read()
        	domWadl = parseString(wadl)
        	resources = domWadl.getElementsByTagName('resource')          
        	for i in range(len(resources)):
        	    self.resources_target.append(self.url+"/"+resources[i].getAttribute('path'))          
     	except:
		out_mess="Error in Dataset.ressources_list() not allowed, please contact admin for more info"
                self.__logger.error(out_mess)		
#Throw a research request on Sitools2 server, inside limit 350000 so > 1 month full cadence for SDO project 
    def search(self,query_list,output_list,sort_list,limit_request=350000, limit_to_nb_res_max=-1, **kwargs) :
	"""This is the generic search() method of a Sitools2 instance.
	The parameters available are : query_list, output_list, sort_list, limit_request & limit_to_nb_res_max.
	Example of use : 
	result=ds1.search([Q1,Q2,Q3,Q4],O1,S1,limit_to_nb_res_max=10) 
	Where Q1, Q2, Q3 & Q4 can be :
	Q1=Query(param_query1)
	Q2=Query(param_query2)
	Q3=Query(param_query3)
	Q4=Query(param_query4)
	Where param _query1, param_query2, param_query3, param_query4 can value :
	param_query1=[[ds1.fields_list[4]],['2012-08-10T00:00','2012-08-10T01:00'],'DATE_BETWEEN']
	param_query2=[[ds1.fields_list[5]],['335'],'IN']
	param_query3=[[ds1.fields_list[10]],['1 min'],'CADENCE']
	param_query4=[[ds1.fields_list[8]],['2.900849'],'LTE']
	"""
	kwargs.update({
		'media' : 'json',
		'limit' : 300,
		'start' : 0
	})
#Initialize counter
	j=0#filter counter
	i=0#p counter
	for num_query,query in enumerate(query_list) :#create url options p[$i] and filter[$j]
		operation=query.operation.upper()#transform entries as upper letter
		if operation =='GE' : 
			operation='GTE'
		elif operation == 'LE' : 
			operation='LTE'
		if operation in ['LT', 'EQ', 'GT', 'LTE', 'GTE'] :
			for field in query.fields_list :
				if field.name not in self.allowed_filter_list :
					err_mess="filter on %s is not allowed" % field.name
                                        self.__logger.error(err_mess)					
					raise Sitools2Exception(err_mess)
			kwargs.update({
			'filter['+str(j)+'][columnAlias]' : "|".join(query.name_list),
			'filter['+str(j)+'][data][type]' : 'numeric',
			'filter['+str(j)+'][data][value]' : "|".join(query.value_list),
			'filter['+str(j)+'][data][comparison]' : operation
			})
			j+=1 #increment filter counter
		elif operation in ['LIKE'] :
			operation='TEXT'
			i+=1#increment p counter
		elif operation in ['IN'] :
			operation='LISTBOXMULTIPLE'
			kwargs.update({
				'p['+str(i)+']' : operation+"|"+"|".join(query.name_list)+"|"+"|".join(query.value_list)
			})
			i+=1#increment p counter
		elif operation in ['DATE_BETWEEN','NUMERIC_BETWEEN', 'CADENCE'] :
			kwargs.update({
				'p['+str(i)+']' : operation+"|"+"|".join(query.name_list)+"|"+"|".join(query.value_list)
			})
			i+=1#increment p counter
		else :
			allowed_operations="ge, le, gte, lte, lt, eq, gt, lte, like, in, numeric_between, date_between"
			err_mess="Operation not available : %s Allowed operations are : %s" % (operation,allowed_operations)
                        self.__logger.error(err_mess)			
			raise Sitools2Exception	(err_mess)
	output_name_list=[]
	output_name_dict={}
	for i, field in enumerate(output_list):#build output object list and output object dict with name as a key  
		output_name_list.append(field.name)
		output_name_dict.update({
			field.name : field
		}
		)
	kwargs.update({#build colModel url options
		'colModel' : '"'+", ".join(output_name_list)+'"'
	})
	sort_dic_list=[]
	for field in sort_list :#build sort output options 
		if field[0].name not in self.allowed_sort_list :
			err_mess="Error in Dataset.search(): sort on %s is not allowed" % field.name		
                        self.__logger.error(err_mess)
			raise Sitools2Exception(err_mess)
		sort_dictionary={}
		sort_dictionary.update({
		"field" : field[0].name ,
		"direction" : field[1]
		})
		sort_dic_list.append(sort_dictionary)
	temp_kwargs={}
	temp_kwargs.update({
				'sort' : {"ordersList" : sort_dic_list}
			})
	temp_url=urllib.urlencode(temp_kwargs).replace('+','').replace('%27','%22')
	url_count=self.url+"/count"+'?'+urllib.urlencode(kwargs)+"&"+temp_url#Build url just for count
	url=self.url+"/records"+'?'+urllib.urlencode(kwargs)+"&"+temp_url#Build url for the request
        self.__logger.debug(urllib.unquote(url_count.encode('ascii')).decode('utf-8'))
	result_count =simplejson.load(urllib.urlopen(url_count))
	nbr_results=result_count['total']
	result=[]
	if nbr_results < limit_request :#Check if the request does not exceed 350 000 items 
		if limit_to_nb_res_max>0 and limit_to_nb_res_max < kwargs['limit']: #if nbr to display is specified and < 300
			kwargs['limit']=limit_to_nb_res_max
			kwargs['nocount']='true'
			nbr_results=limit_to_nb_res_max
			url=self.url+"/records"+'?'+urllib.urlencode(kwargs)+"&"+temp_url
		elif  limit_to_nb_res_max>0 and  limit_to_nb_res_max >= kwargs['limit']:#if nbr to display is specified and >= 300
			nbr_results=limit_to_nb_res_max
			kwargs['nocount']='true'
			url=self.url+"/records"+'?'+urllib.urlencode(kwargs)+"&"+temp_url
		while (nbr_results-kwargs['start'])>0 :#Do the job per 300 items till nbr_result is reached
#Check that request is done each 300 items
			result_temp =simplejson.load(urllib.urlopen(url))
	 		for data in result_temp['data'] :
                                self.__logger.debug(data)
				result_dict={}
				for k,v in data.items() :                                       
					if (k not in self.noClientAccess_list and k != 'uri' and k in output_name_list) or k in output_name_list :
                                                self.__logger.debug(output_name_dict)
                                                self.__logger.debug("key to search = "+ k)                                                
						if output_name_dict[k].type.startswith('int'): 
							result_dict.update({
								k : int(v)
							})
						elif output_name_dict[k].type.startswith('float'):
							result_dict.update({
								k : float(v)
							})
						elif output_name_dict[k].type.startswith('timestamp'):
							(dt, mSecs)= v.split(".")
							dt = datetime.strptime(dt,"%Y-%m-%dT%H:%M:%S")
							mSeconds = timedelta(microseconds = int(mSecs))
							result_dict.update({
								k : dt+mSeconds
							})
						else :
							result_dict.update({
								k : v
							})
				result.append(result_dict)
			kwargs['start'] += kwargs['limit']#increment the job by the kwargs limit given (by design)  
			url=self.url+"/records"+'?'+urllib.urlencode(kwargs)+"&"+temp_url#encode new kwargs and build new url for request                        
		return result
	else :
		out_mess="Not allowed\nNbr results (%d) exceeds limit_request param: %d\n" % (result_count['total'],limit_request)
                self.__logger.info(out_mess)
		sys.stdout.write(out_mess)
		return result
#Output attributes of Dataset
    def display(self) :
	print self.__repr__()
#Representation of an instance of Dataset
    def __repr__(self):
	phrase=""
	phrase+="\n\nDataset object display() :\n\t%s\n\t\tdescription : %s\n\t\turi : %s\n\t\turl : %s\n\t\tprimary_key : %s" % (self.name,self.description,self.uri,self.url,self.primary_key.name)
	phrase+="\n\t\tresources_list :"
	for i, res in enumerate(self.resources_target) :
		phrase+="\n\t\t\t%d) %s" % (i,res)	
	phrase+="\n\t\tfields list :"
	for i, field in enumerate(self.fields_list) :
		phrase+="\n\t\t\t%d) %s" % (i,field.name)	
	phrase+="\n\t\tfilter list :"
	for i, field in enumerate(self.filter_list) :
		phrase+="\n\t\t\t%d) %s" % (i,field.name)	
	phrase+="\n\t\tsort list :"
	for i, field in enumerate(self.sort_list) :
		phrase+="\n\t\t\t%d) %s" % (i,field.name)
	return phrase

    def execute_plugin(self, plugin_name=None, pkey_list=[], FILENAME=None, **kwargs) :
	resources_list=[]
	if plugin_name is None :
		err_mess="Error execute_plugin(): No plugin_name provided"
                self.__logger.error(err_mess)		
		raise Sitools2Exception(err_mess)
	for resource in self.resources_target :
		resources_list.append(resource.split("/")[-1])
	if plugin_name not in resources_list : 
			err_mess="Error execute_plugin(): This plugin_name %s does not exist in %s dataset" % (plugin_name,self.name)
			self.__logger.error(err_mess)	
			raise Sitools2Exception(err_mess)
	if len(pkey_list)==0 :
		err_mess="Error execute_plugin(): No identifiers pkey provided"
                self.__logger.error(err_mess)			
		raise Sitools2Exception(err_mess)
	if FILENAME is None :
		err_mess="Error execute_plugin(): No FILENAME provided"
		self.__logger.error(err_mess)	
		raise Sitools2Exception(err_mess)
	operation='LISTBOXMULTIPLE'
	kwargs.update({
		'p[0]' : operation+"|"+self.primary_key.name+"|"+"|".join(str(pkey) for pkey in pkey_list)
	})
	url=self.url+"/"+plugin_name+"?"+urllib.urlencode(kwargs)
        self.__logger.debug(urllib.unquote(url.encode('ascii')).decode('utf-8'))	
	return urllib.urlretrieve('%s' % url, FILENAME)

class Project:
    """Define a Project class.
       A Project instance gives details about a project of Sitools2. 
       It has the following attributes : name, description, uri, url, resources_target.
       The method dataset_list() will return information about the number of datasets available, their name and uri.
    """
#Initialize Project
    def __init__(self, url):
        self.__logger = _Log.getLogger(self.__class__.__name__)
        self.name = ""
	self.description = ""
	self.uri = "/"+url.split("/")[-1]
        self.url = url
	self.resources_target = []
	self.__compute_attributes()
        self.resources_list();
#Compute_attributes builds value for instance Project
    def __compute_attributes(self,**kwargs) :
	kwargs.update({
		'media' : 'json'
	})
	url=self.url+'?'+urllib.urlencode(kwargs)
        self.__logger.debug(urllib.unquote(url.encode('ascii')).decode('utf-8'))
	result =simplejson.load(urllib.urlopen(url))
	self.name=result['project']['name']
	self.description=result['project']['description']
#Explore Project resources (method=options should be allowed)
    def resources_list(self):
	        url = urllib.urlopen(self.url+'?method=OPTIONS')      
        	wadl = url.read()
		try :
        		domWadl = parseString(wadl)
		except :
			out_mess="Project : project.resources_list() not allowed, please contact admin for more info"
                        self.__logger.info(out_mess)			
		else : 
        		resources = domWadl.getElementsByTagName('resource')          
        		for i in range(len(resources)):
        		    self.resources_target.append(self.url+"/"+resources[i].getAttribute('path'))          
#Ouptut Project attributes       
    def display(self):
	print self.__repr__()
#Represention of Project instance 
    def __repr__(self):
	phrase=""
	phrase+="\n\nProject object display() :\n\t%s\n\t\tdescription : %s\n\t\turi : %s\n\t\turl : %s" % (self.name,self.description,self.uri,self.url) 
	phrase+="\n\t\tresources list :"
	if len(self.resources_target)!=0 :
		for i, res in enumerate(self.resources_target) :
			phrase+="\n\t\t\t%d) %s" % (i,res)
	return phrase

#List all datasets in the Project and create the dataset objects
    def dataset_list(self, **kwargs):
	"""Return relevant information concerning the datasets of your project
	"""
	sitools_url=self.url.split("/")[0]+"//"+self.url.split("//")[1].split("/")[0]
	kwargs.update({
		'media' : 'json'
	})
	url=self.url+'/datasets'+'?'+urllib.urlencode(kwargs)
	data=[]
	try:
		result =simplejson.load(urllib.urlopen(url))
		if len (result['data'])!=0 :
			for i,dataset in enumerate(result['data']) :
				ds_url=sitools_url+dataset['url']
				data.append(Dataset(ds_url))
	except :
		out_mess="Cannot dataset %s is protected\nContact admin for more info" % url
                self.__logger.error(out_mess)
	return data
