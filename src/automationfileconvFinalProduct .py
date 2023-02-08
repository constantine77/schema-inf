# -*- coding: utf-8 -*-
"""AutomationFileConv.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qq_wGpYpj9L3Al474Aq8EWXhHSFRy0um
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import ntpath
import json
from fastavro import reader as rd, json_writer
import csv
import sys
import pprint
from collections import defaultdict

#Function to get the filename from path for both Window/Linux system.
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def conversion_json(path):
  #Spliting filename with the extention for the output file
  fname = path_leaf(path)
  fname = fname.split('.')[0]
  if path.endswith('.avro'):
    with open(fname+".json", "w") as json_file:
      with open(path, "rb") as avro_file:
          avro_reader = rd(avro_file)
          json_writer(json_file, avro_reader.writer_schema, avro_reader)
    json_file.close() 
    avro_file.close()
    #Reformatting your JSON file to contain an array
    newJson = [json.loads(line) for line in open(fname+'.json','r')]
    #The json file where the output must be stored 
    out_file = open(fname+".json", "w") 
    #Dump json data into the output file with indent = 6    
    json.dump(newJson, out_file,indent=6) 
    out_file.close()
  elif path.endswith('.parquet'):
    # Reading PARQUET data as Dataframe with Pyarrow
    dataFrame = pd.read_parquet(path, engine='fastparquet')
    result = dataFrame.to_json(orient="records")
    parsed = json.loads(result)
    # json.dumps(parsed, indent=4)
    out_file = open(fname+".json", "w")  
    json.dump(parsed, out_file,indent=6) 
    out_file.close()
  else:
    #Read csv file and add to data
    data = {}
    count = 0
    with open(path) as csvFile:
      csvReader = csv.DictReader(csvFile)
      for rows in csvReader:
        data[count] = rows
        count += 1
    csvFile.close()
    #Create new json file and write data on it
    with open(fname+'.json','w') as jsonFile:
      jsonFile.write(json.dumps(data, indent=4))
    jsonFile.close()

def createArraySchema(array_val):
	'''
	Arrays add an unfortuante amount of complexity to this. So we search for the type and the act accordingly.
	the assumption is made that the array is all of the same type to avoid extra computation.
	TODO; find a way to avoid duplicate code for the if statements finding which type it is
	'''
	## get type of array_val
	arr_type = type(array_val)

	## check type
	if arr_type is dict:
		return createSchema(array_val)
	elif arr_type is int: 
		return "Int"
	if arr_type is float:
		return "Float"
	elif arr_type is bool:
		return "Boolean"
	elif arr_type is str or arr_type is bytes:
		return "String"

def createSchema(df):
	'''
	Loop through keys and create a dctionary that will represent the schema for the document. Recursively call on dictiaonarys to go down object.

	'''
	
	schema = {}
	temp = {}
	count = 0
	colum = df.columns
	for col in colum:
		for row in df[col]:
			if type(row) is int:
				if 'Int' in temp: 
					temp['Int'] +=1
				else:
					temp['Int'] = 1
			elif type(row) is float:
				if 'Float' in temp: 
					temp['Float'] +=1
				else:
					temp['Float'] = 1
			elif type(row) is bool:
				if 'Boolean' in temp: 
					temp['Boolean'] +=1
				else:
					temp['Boolean'] = 1
			elif type(row) is str or type(row) is bytes:
				if 'String' in temp: 
					temp['String'] +=1
				else:
					temp['String'] = 1
			elif type(row) is list:
				if 'List' in temp: 
					temp['List'] +=1
				else:
					temp['List of Type :'+createArraySchema(row)] = 1
			elif type(row) is dict:
				if 'Dictionary' in temp: 
					temp['Dictionary'] +=1
				else:
					temp['Dictionary'] = 1
			else:
				if 'NULL' in temp: 
					temp['NULL'] +=1
				else:
					temp['NULL'] = 1
		max_val = max(temp.values())
		max_key = max(temp, key=temp.get)
		schema[col] = max_key
		temp = {}
	return schema

# 	## create object schema
# 	schema = {}
  
# 	## loop through keys
# 	for key in doc:
# 		## get key type
# 		key_type = type(doc[key])

# 		## change key from unicode to string
# 		key = str(key)

# 		## Check which type this is
# 		if key_type is int:
# 			schema[key] = "Int"
# 		if key_type is float:
# 			schema[key] = "Float"
# 		elif key_type is bool:
# 			schema[key] = "Boolean"
# 		elif key_type is str or key_type is bytes:
# 			if len(doc[key].strip()):
# 				schema[key] = "String"
# 		elif key_type is list:
# 			## create array and add to current schema
# 			schema[key] = [createArraySchema(doc[key][0])]
# 		elif key_type is dict:
# 			## create object and add to current schema
# 			schema[key] = createSchema(doc[key])
# 		else:
# 			print("unknown type:", key_type)

# 	## return fnished schema
# 	return schema


# def getSchema(file_name):
# 	'''
# 	Open file and pass the json document to createSchema
# 	'''
# 	with open(file_name) as data_file:    
# 		doc = json.loads(data_file.read()) 
# 		for key in doc:
# 				return createSchema(key)

if __name__ == "__main__":
	file_name = ""
	schema = defaultdict(list)
	count = 'schema'
	## test if file name given in command line
	if len(sys.argv) == 2:
		## grab from command line
		file_name = sys.argv[1]
	else:
		## Get file from user
		file_name = input("Please enter file name: ")
		fname = path_leaf(file_name)
		fname = fname.split('.')[0]
		if file_name.endswith('.json'):
			df = pd.read_json(file_name)
			schem = createSchema(df) 
			# with open(file_name) as data_file:    
			# 	doc = json.loads(data_file.read()) 
			# 	for schema in doc:
			# 		sch = createSchema(schema)
			# 		schema[doc] = sch
			#Create new json file and write data on it
			with open('schema'+fname+'.json','w') as jsonFile:
				jsonFile.write(json.dumps(schem, indent=4))
			jsonFile.close()
		else:
				conversion_json(file_name)
				df = pd.read_json(fname+'.json')
				schem = createSchema(df)
				# with open(fname+'.json') as data_file:
				# 	doc = json.loads(data_file.read())
				# 	df = pd.read_json (r'usrdata')
				# 	for key in doc:	
				# 		sch = createSchema(key)
				# 		schema[count] = sch
				# 		print(sch)
				#Create new json file and write data on it
				with open('schema'+fname+'.json','w') as jsonFile:
					jsonFile.write(json.dumps(schem, indent=4))
				jsonFile.close()

# df = pd.read_json (r'userDataParquet.json')
# schema = {}
# arr = {}
# count = 0
# colum = df.columns
# for col in colum:
#   for row in df[col]:
#     if type(row) is int:
#       if 'Int' in arr: 
#         arr['Int'] +=1
#       else:
#         arr['Int'] = 1
#     elif type(row) is float:
#       if 'Float' in arr: 
#         arr['Float'] +=1
#       else:
#         arr['Float'] = 1
#     elif type(row) is bool:
#       if 'Boolean' in arr: 
#         arr['Boolean'] +=1
#       else:
#         arr['Boolean'] = 1
#     elif type(row) is str or type(row) is bytes:
#       if 'String' in arr: 
#         arr['String'] +=1
#       else:
#         arr['String'] = 1
#     elif type(row) is list:
#       if 'List' in arr: 
#         arr['List'] +=1
#       else:
#         arr['List of Type :'+createArraySchema(row)] = 1
#     elif type(row) is dict:
#       if 'Dictionary' in arr: 
#         arr['Dictionary'] +=1
#       else:
#         arr['Dictionary'] = 1
#     else:
#       if 'NULL' in arr: 
#         arr['NULL'] +=1
#       else:
#         arr['NULL'] = 1
#   max_val = max(arr.values())
#   max_key = max(arr, key=arr.get)
#   schema[col] = max_key
#   arr = {}

# schema
# 

