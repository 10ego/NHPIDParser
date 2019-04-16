## Elastic indexing script using NHPIDParser
import NHPIDParser
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from multiprocessing import Pool
import numpy as np
## parent organism id exists up to 5184 records
## ingredient id exists up to 17606 records
## syn? id exists up to 42204 records
## org id exists up to 2812 records

es = Elasticsearch(YOUR_ELASTIC_URL, timeout = 100)
nhp = NHPIDParser.parse('ingredient') # Parse the ingredients section

def buildJobs(max_id):
	return np.arange(1, int(max_id)+1)

def indexES(id_no):
	data = nhp.fetch(id_no)
	es.index(index = "nhpid_ing", doc_type = "foo", body = data, timeout='5m')
	print("Index complete on {}".format(id_no))

id_list = buildJobs(17606)

with Pool(25) as p:
	p.map(indexES, id_list)