# -----------------------------------------------------------------
# Plugin for Mongo DB used to store data 
# -----------------------------------------------------------------
from pymongo import MongoClient
import ast

class BetSportsDB(object):
  """
  Mongo DB interface for Ultra-M health monitoring.
  """

  def __init__(self, host, port, identity, logger = None):
    db_client = MongoClient(host, port)
    db_client.db = db_client[identity]
    self.db_tbl = db_client.db.tbl
    self.identity = identity
    self.client = db_client
    self.logger = logger

  def fix_id(self, client_id):
    fix_id = client_id.replace(':', '_').replace('.', '_').replace('/', '_')
    id = "".join(fix_id.split())
    return id
    

  def debug(self, err):
    if self.logger:
      self.logger.debug(err)
    else:
      print err

  def read_entry(self, cl_id):
    id = self.fix_id(cl_id)
    try:
      item = self.db_tbl.find_one({"_id": id})
      if item:
        return  ast.literal_eval(item['data'])
      return None
    except Exception as m_exp:
      self.debug("Could not get the data for ID: %s, got exception from mongodb: %s" % (id, m_exp))
      return None

  def destroy(self):
    try:
      self.client.drop_database(self.identity)
    except Exception as m_exp:
      self.debug("Could not destry %s, got exception from mongodb: %s" % (self.identity, m_exp))


  def write_entry(self, cl_id, data, update=True):
    id = self.fix_id(cl_id)


    try:
      db_tbl = self.db_tbl.find_one({'_id': id})
    except Exception as m_exp:
      self.debug("Could not get the data for ID: %s, got exception from mongodb: %s" % (id, m_exp))
      return None

    if db_tbl:
      if update:
        try:
          self.db_tbl.update({'_id': id}, {'data': str(data)})
        except Exception as m_exp:
          self.debug("Could not update the data for ID: %s, got exception from mongodb: %s" % (id, m_exp))
      else:
        return False    
    else:  
      item = dict(_id=id, data=str(data))
      try:
        self.db_tbl.insert_one(item)
      except Exception as m_exp:
        self.debug("Could not set the data for ID: %s, got exception from mongodb: %s" % (id, m_exp))
    return True

  def delete_entry(self, cl_id):
    id = self.fix_id(cl_id)
    try:
      self.db_tbl.delete_one({'_id': id})
    except Exception as m_exp:
      self.debug("Could not delete entry for ID: %s, got exception from mongodb: %s" % (id, m_exp))

  def get_all_ids(self):
    try:
      db_iter = self.db_tbl.find({}, {'_id': 1})
      return list(db_iter)
    except Exception as m_exp:
      self.debug("Could not get all entry IDs, exception from mongodb: %s" % m_exp)
      return []


  def get_id_index(self, cl_id):
     id = self.fix_id(cl_id)
     entries = self.get_all_ids()
     id_index =  next((idx for idx, entry in enumerate(entries) if id == entry['_id']), None)
     return id_index
      
  def read_all(self):
    all_entries = [ ast.literal_eval(entry['data']) for entry in self.db_tbl.find() if entry]
    return all_entries

