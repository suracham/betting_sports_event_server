#!/usr/bin/python
#------------------------------------------------------------------
# HTTP server
#------------------------------------------------------------------
import sys
import os
from flask import Flask, make_response, jsonify, send_from_directory, request
from flask.views import MethodView
sys.path.append(os.path.abspath('plugins'))
sys.path.append(os.path.abspath('utils'))
import multiprocessing
from mdb import mdb_interface
from logger_interface.logger import get_logger
from utils import helpers
from datetime import datetime
import argparse

app = Flask(__name__)
DEFAULT_MONGO_DB_IP = '127.0.0.1'
DEFAULT_MONGO_DB_PORT = 27017
VERSION='1.0'

class BetSportAPI(MethodView):
  BET_DATA_LOG_FILE = "./bet_data.log"
  NEW_EVENT = "NewEvent"
  UPDATE_ODDS = "UpdateOdds"
  SUPPORTED_MESSAGES = ["NewEvent", "UpdateOdds"]


  def __init__(self):

    log_dir = os.path.dirname(BetSportAPI.BET_DATA_LOG_FILE)
    if not os.path.isdir(log_dir):
      os.makedirs(log_dir)

    self.logger = get_logger('BET_SPORT_API_SERVER', BetSportAPI.BET_DATA_LOG_FILE)
    self.db_handle = mdb_interface.BetSportsDB(DEFAULT_MONGO_DB_IP, DEFAULT_MONGO_DB_PORT, 'BET_SPORTS_DATA', self.logger)

  def debug(self, msg):
    if self.logger:
      self.logger.debug(msg)
    else:
      print msg

  def validate_new_event(self, new_event, msg_type=NEW_EVENT):
    """
    Validates the New Event information as per requirements
    """
    if not new_event.get('id') or not new_event.get('message_type') or \
       not new_event.get('event'):
       return False, None
    elif new_event.get('message_type') != msg_type:
       return False

    helpers.dict_key_to_correct_type(new_event)

    return True

  def filter_events(self, query):
    all_events = self.db_handle.read_all()
    if not all_events:
      return None
    match_evnts = []

    for evnt in all_events:
      # filter the keys which are present both in event & query
      keys = set(evnt.keys()) & set(query.keys())
      for key in keys:
        if evnt[key] != query[key]:
          break
      else:
        match_evnt = {'id': evnt['id'], 
                      'url':evnt['url'], 
                      'name':evnt['name'], 
                      'startTime':evnt['startTime']}
        match_evnts.append(match_evnt)
    return match_evnts    

  def get_events_in_order(self, ord_key):
    all_events = self.db_handle.read_all()
    if not all_events:
      return None

    match_evnts = []
    if ord_key != 'startTime': 
      sort_events = sorted(all_events, key=lambda k: k[ord_key]) 
    else:
      sort_events = sorted(all_events, key=lambda k:datetime.strptime(k['startTime'],'%Y-%m-%d %H:%M:%S'))
     
    for evnt in sort_events:
      match_evnt = {'id': evnt['id'], 
                    'url':evnt['url'], 
                    'name':evnt['name'], 
                    'startTime':evnt['startTime']}
      match_evnts.append(match_evnt)
    return match_evnts

  def get(self, match_id=None):
    """
    This function returns the data with matchid or query
    """
    # Get data with Match ID
    if match_id == None:
      if not len(request.args): 
        return self.response('Match Id not provided', 404)
      # get result based on query 
      query = helpers.unicode_to_str(request.args.to_dict())
      result = None
      if query.has_key('ordering'):
        if query['ordering'] in ['startTime', 'id', 'name']:
          result = self.get_events_in_order(query['ordering'])
        else:
          error = "Ordering can't be done with provided information"
      else:
        result = self.filter_events(query)
      error = "No information found for query %s"%(str(query))
    else:
      result = self.db_handle.read_entry(str(match_id))
      error = "Event with Match ID not available"
        
    if not result:
      return self.response(error, 404)

    return make_response(jsonify(result), 200)

  def delete(self, match_id=None):
    """
    This function deletes the event with matchid 
    """
    if match_id == None:
      return self.response('Match Id not provided', 404)
    
    self.db_handle.delete_entry(str(match_id))

    return self.response('Deleted Event', 200)


  def create_event(self):
    new_event = helpers.unicode_to_str(request.form.to_dict())
    self.debug("Received New Event for Creation: %s"%(new_event))
    res = self.validate_new_event(new_event)

    if not res:
      self.debug("New Event Validation failed")
      return self.response('Event Information is not correct', 404)

    # Add Event to DB
    new_event['event']['url'] = request.url_root + 'api/match/' + str(new_event['event']['id'])
    result = self.db_handle.write_entry(str(new_event['event']['id']), new_event['event'],\
                                        (request.method == 'PUT'))

    if not result:
      self.debug("Loading Event to DB failed")
      return self.response('Unable to create new Event', 500)

    return self.response("Created Event", 200)
    

  def post(self):
    return self.create_event()

  def put(self):
    if '/match/createevent'.startswith(request.path):
       return self.create_event()

    new_event = helpers.unicode_to_str(request.form.to_dict())

    if not self.validate_new_event(new_event, BetSportAPI.UPDATE_ODDS):
      self.debug("New Event Validation failed")
      return self.response('Provided Information is not correct', 404)

    db_event = self.db_handle.read_entry(str(new_event['event']['id']))
    if not db_event:
      return self.response('Event not avaialable with provided Id', 404)    

    db_event_mkt = {}
    for ind, mkt in enumerate(db_event.get('markets', [])):
      db_event_mkt[mkt['id']] = {'list_id':ind, 'selections': mkt.get('selections', [])}
 
    # update odds in DB Event and store back
    for mkt_id, mkt in enumerate(new_event['event'].get('markets', [])):
      if not mkt['id'] in db_event_mkt:
        continue
      for sel in new_event['event']['markets'][mkt_id].get('selections', []):
        for ind, db_sel in enumerate(db_event_mkt[mkt['id']].get('selections', [])):
           if sel['id'] == db_sel['id'] and sel['name'] == db_sel['name'] and sel.get('odds'):
             mkt_list_id = db_event_mkt[mkt['id']]['list_id']
             db_event['markets'][mkt_list_id]['selections'][ind]['odds'] = sel['odds']
        
    result = self.db_handle.write_entry(str(new_event['event']['id']), db_event, True)

    if not result:
      return self.response('Unable to update Odds', 500)

    return self.response("Updated Odds successfully", 200)

  @staticmethod
  def response(status_msg, http_rc):
    """Wrap the response generation.
    :param http_rc: an HTTP code, e.g. 404
    :param status_msg: a human-friendly message
    """
    json_blob = jsonify({'status': status_msg})
    resp = make_response(json_blob, http_rc)
    return resp

def start_rest_interface(opts):
  rest_interface_view = BetSportAPI.as_view('bet_sport_api')

  # Default GET rule to retrieve match data
  app.add_url_rule('/api/match/<int:match_id>', 
                   view_func=rest_interface_view,
                   methods=['GET'])

  app.add_url_rule('/api/match/', 
                   view_func=rest_interface_view,
                   methods=['GET'])

  app.add_url_rule('/api/match/createevent', 
                   view_func=rest_interface_view,
                   methods=['POST', 'POST'])

  app.add_url_rule('/api/match/updateodds', 
                   view_func=rest_interface_view,
                   methods=['PUT'])

  app.add_url_rule('/api/match/deleteevent/<int:match_id>', 
                   view_func=rest_interface_view,
                   methods=['DELETE'])

  # use_reloader=False stops the debug setting from enabling
  app.run(host=opts.server_ip, port=opts.server_port, 
          debug=True, use_reloader=False)

def get_opts():
  """
  Parse and get options provied by user either via command line
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--version', action='version', version=VERSION)
  parser.add_argument('--server-ip', dest='server_ip', default='0.0.0.0',
                      help="IP to which WSGI server should be binded")
  parser.add_argument('--server-port', dest='server_port', default=5000, type=int,
                      help="PORT to which WSGI server should be binded")

  parser.add_argument('--db-ip', dest='db_ip', default='127.0.0.1',
                      help="DB IP to connect")

  parser.add_argument('--db-port', dest='db_port', default=27017, type=int,
                      help="DB PORT to connect")

  args = parser.parse_args()

  global DEFAULT_MONGO_DB_IP
  global DEFAULT_MONGO_DB_PORT
  DEFAULT_MONGO_DB_IP = args.db_ip
  DEFAULT_MONGO_DB_PORT = args.db_port


  return args

if __name__ == "__main__":
  opts = get_opts()  
  start_rest_interface(opts)



  

