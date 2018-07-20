import sys, os
import requests
import re
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

class IdNotFoundError(ValueError):
    pass

class DbCrawler(object):
    
    def __init__(self):
        super(DbCrawler, self).__init__()
        self.picr_address = 'http://www.ebi.ac.uk/Tools/picr/rest/'
        self.uniprot_address = 'http://www.uniprot.org/uniprot/'
        self.headers = {'User / Agent' : 'Python a.murachelli@nki.nl'}


    def query_picr_by_id(self, id_, database):
        '''
        Given a sequence ID, queries PICR to get the corresponding id_ from the 
        specified database. (http://www.ebi.ac.uk/Tools/picr/)
        Usually succesful for uniprot, not tested for "weird" databases.
        Returns the GET response 
        '''
        query ='getUPIForAccession?accession={}&database={}'.format(id_, database)
        req = '{}{}'.format(self.picr_address,query)
        self.headers["Content-Type"] = "application/xml"
        return self.REST_query(req, self.headers)
    
    def REST_query(self, req, headers):
        '''
        Runs GET requests and returns the response
        Raises error on 4xx or 5xx status 
        '''
        r = requests.get(req, headers=headers)
        if not r.ok:
            r.raise_for_status() #raises the appropriate errors if 4xx or 5xx 
        return r 
    
    def get_uniprot_id_from_id(self, id_):
        '''
        Maps any protein id to a UNIPROT protein id, and returns it.
        Raises IdNotFoundError if no id is found
        '''
        response = self.query_picr_by_id(id_, 'TREMBL')
        soup = BeautifulSoup(response.text, 'xml')
        regexp = re.compile(r'.*accession')
        entry = soup.find_all(regexp) 
        if not entry:
            msg = ('Id {id} not found'.format(id_))
            raise IdNotFoundError(msg)
        return entry[0].text
    
    def fetch_uniprot_entry(self, id_):
        '''
        Retrieve the uniprot entry corresponding to id_ from uniprot.
        Returns a Beautifulsoup of the entry
        '''
        req = '{}{}.xml'.format(self.uniprot_address, id_)
        response = self.REST_query(req, headers={}) 
        return BeautifulSoup(response.text, 'xml')
    
    def uniprot_acc_to_uniprot_id(self, id_):
        '''
        Maps a uniprot accession id to a entrez gene accession id
        '''
        url = 'http://www.uniprot.org/uploadlists/'
        params = {
        'from':'GENENAME',
        'to':'ID',
        'format':'tab',
        'query':id_
        }
        page = self.urllib_query(url, params)
        gene_id =str(page).split('\t')[-1].strip()
        return page #gene_id
    
    def urllib_query(self, url, params):
        data = urlencode(params).encode('utf-8')
        request = Request(url, data)
        request.add_header('User-Agent', 'Python %s' % 'a.murachelli@nki.nl')
        response = urlopen(request)
        page = response.read(200000)
        page = BeautifulSoup(page)
        return page
    
    

path = r'/home/andrea/Downloads/'
fasta_in = r'ENSGT00510000046640_gene_tree.fa'
with open(os.path.join(path + fasta_in), 'r+') as f:
    alignment = f.read().split('\n')
accessions = {}
for line in alignment:
    if line.startswith('>'):
        acc_id = line.split('_')[0][1:]
        accessions[acc_id] = ''

id_ = list(accessions.keys())[2]
print(id_)
a = DbCrawler()
entry = a.get_uniprot_id_from_id(id_)
print(entry)
primary_acc = a.uniprot_acc_to_uniprot_id(id_)
print(primary_acc)
# soup = a.fetch_uniprot_entry(primary_acc)
# print(soup.prettify())

