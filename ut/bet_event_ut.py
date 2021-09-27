import unittest
import requests
import json
import sys
import urllib
import urllib2
import ast

class TestFlaskApiUsingRequests(unittest.TestCase):
    def setUp(self):
       self.maxDiff = None
       # No check added since UT expects the test profiles available
       with open('./new_event.json') as f:
         self.test_new_event = json.load(f)

       with open('./new_event_2.json') as f:
         self.test_new_event_2 = json.load(f)

       with open('./update_odds.json') as f:
         self.test_update_odds = json.load(f)

    def test_1_post_event_1(self):
        url = 'http://127.0.0.1:1234/api/match/createevent'
        data = urllib.urlencode(self.test_new_event)
        req = urllib2.Request(url, data)
        req.get_method = lambda: 'POST'
        response = urllib2.urlopen(req).read()
        print ast.literal_eval(response)
        self.assertEqual(ast.literal_eval(response), {'status': 'Created Event'})

    def test_2_post_event_2(self):
        url = 'http://127.0.0.1:1234/api/match/createevent'
        data = urllib.urlencode(self.test_new_event_2)
        req = urllib2.Request(url, data)
        req.get_method = lambda: 'POST'
        response = urllib2.urlopen(req).read()
        print ast.literal_eval(response)
        self.assertEqual(ast.literal_eval(response), {'status': 'Created Event'})

    def test_3_update_odds_event_1(self):
        url = 'http://127.0.0.1:1234/api/match/updateodds'
        data = urllib.urlencode(self.test_update_odds)
        req = urllib2.Request(url, data)
        req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req).read()
        print response
        self.assertEqual(ast.literal_eval(response), {'status': 'Updated Odds successfully'})

    def test_4_get_data_by_id(self):
        # Get Events by MatchID
        validation_checks = {self.test_new_event['event']['id']: self.test_update_odds['event'],
                             self.test_new_event_2['event']['id']: self.test_new_event_2['event']}
        for id in [self.test_new_event['event']['id'], self.test_new_event_2['event']['id']]:
          url = 'http://127.0.0.1:1234/api/match/%s'%(id)
          data = urllib.urlencode(self.test_update_odds)
          req = urllib2.Request(url, data)
          req.get_method = lambda: 'GET'
          response = urllib2.urlopen(req).read()
          response = ast.literal_eval(response)
          response.pop('url', None)
          self.assertEqual(response, validation_checks[id])

    def test_5_get_data_by_startTime(self):
        valid_res = '[\n  {\n    "id": 994839351840, \n    "name": "Cavaliers vs Lakers", \n    "startTime": "2021-01-15 22:00:00", \n    "url": "http://127.0.0.1:1234/api/match/994839351840"\n  }, \n  {\n    "id": 994839351740, \n    "name": "Real Madrid vs Barcelona", \n    "startTime": "2021-06-20 10:30:00", \n    "url": "http://127.0.0.1:1234/api/match/994839351740"\n  }\n]\n'
        url = 'http://127.0.0.1:1234/api/match/?ordering=startTime'
        data = urllib.urlencode(self.test_update_odds)
        req = urllib2.Request(url, data)
        req.get_method = lambda: 'GET'
        response = urllib2.urlopen(req).read()
        print response
        self.assertEqual(response, valid_res)

    def test_6_get_data_by_id(self):
        valid_res = '[\n  {\n    "id": 994839351740, \n    "name": "Real Madrid vs Barcelona", \n    "startTime": "2021-06-20 10:30:00", \n    "url": "http://127.0.0.1:1234/api/match/994839351740"\n  }, \n  {\n    "id": 994839351840, \n    "name": "Cavaliers vs Lakers", \n    "startTime": "2021-01-15 22:00:00", \n    "url": "http://127.0.0.1:1234/api/match/994839351840"\n  }\n]\n'
        url = 'http://127.0.0.1:1234/api/match/?ordering=id'
        data = urllib.urlencode(self.test_update_odds)
        req = urllib2.Request(url, data)
        req.get_method = lambda: 'GET'
        response = urllib2.urlopen(req).read()
        print response
        self.assertEqual(response, valid_res)

    def test_7_get_data_by_keys(self):
        valid_res = '[\n  {\n    "id": 994839351740, \n    "name": "Real Madrid vs Barcelona", \n    "startTime": "2021-06-20 10:30:00", \n    "url": "http://127.0.0.1:1234/api/match/994839351740"\n  }\n]\n'
        url = 'http://127.0.0.1:1234/api/match/?name=Real%20Madrid%20vs%20Barcelona'
        data = urllib.urlencode(self.test_update_odds)
        req = urllib2.Request(url, data)
        req.get_method = lambda: 'GET'
        response = urllib2.urlopen(req).read()
        print response
        self.assertEqual(response, valid_res)


    def test_8_delete_event(self):
     # Delete Events
     for id in [self.test_new_event['event']['id'], self.test_new_event_2['event']['id']]:
       url = 'http://127.0.0.1:1234/api/match/deleteevent/%s'%(id)
       req = urllib2.Request(url)
       req.get_method = lambda: 'DELETE'
       response = urllib2.urlopen(req).read()
       print response
     self.assertEqual(ast.literal_eval(response), {'status': 'Deleted Event'})

if __name__ == "__main__":
    unittest.main()
