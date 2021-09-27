# Sports Events Betting Management Server 

It is a sports betting platform. The main functional areas are:

- Manages data about sporting events to allow users to place bets.

- Provide APIs to receive data from external providers and update our system with the latest data about events in real time.

- Provide access to support team to allow them to see the most recent data for each event and to query data.


## Installation

Clone the repository using git

```bash
git clone https://github.com/suracham/betting_sports_event_server
```

## Starting Betting Sporting events management server

```bash
./bet_sport_event_rest_api_intf.py –server-ip <SERVER_IP> –server-port <SERVER_PORT> --db-ip <DB_IP> --db-port <DB_PORT>
```
Command line options are not mandatory i.e. if any option is missed, default value will be used.

It provides the help information as below:

```bash
./bet_sport_event_rest_api_intf.py --help
usage: args.py [-h] [--version] [--server-ip SERVER_IP]
               [--server-port SERVER_PORT] [--db-ip DB_IP] [--db-port DB_PORT]
optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --server-ip SERVER_IP
                        IP to which WSGI server should be binded
  --server-port SERVER_PORT
                        PORT to which WSGI server should be binded
  --db-ip DB_IP         DB IP to connect
  --db-port DB_PORT     DB PORT to connect 
```

### Example
```bash
 python ./bet_sport_event_rest_api_intf.py --server-ip 0.0.0.0 --server-port 1234 --db-ip 127.0.0.1 --db-port 27017
```

Note: Refer Dependencies section before starting the application

## DEVELOPER USE Information
### DB Plugin
Application uses MongoDB to store information about sports events, it can be changed to any DB without changing the application code i.e. it uses MongoDB plugin rather than direct Python MongoDB APIs. DB plugin implements the wrapper functions around the Python MongoDB APIs, so to change MongoDB to other DB only the new DB plugin should be implemented with same APIs. 

### Logging
All logging information is redirected to the file /var/log/betserver/bet_data.log. It supports logging on console i.e. stdout
Note: logrotate.conf file can be updated for log rotation of the file /var/log/betserver/bet_data.log

### Unit Test
Unit tests are present in the directory ut. Present testcases tests the all API functionalities i.e. GET, POST, PUT, DELETE corresponding to events. 

Run the unit tests using below command
```bash
python bet_event_ut.py
```

## APIs Summary

|    API  |   Method Type  |  Description  |
| ------------ | ------------ | ------------ |
|  /api/match/createevent  | POST, PUT  |  It creates the sporting event with the provided information. If PUT method is used to update already created event, it doesn’t update any information.   |
|  /api/match/updateodds | PUT    |  Updates the odds information of the already created sporting event.   |
|  /api/match/<int:id>  | GET  |  It provides the event information corresponding to provided match ID  |
|  /api/match/updateodds | PUT    |  Updates the odds information of the already created sporting event.   |
|  /api/match/?<Query Arguments>  | GET  |  It provides the events’ information corresponding to query. Supported queries are: (i) ordering=<key> : key should be the properties of event i.e. startTime, id, name (ii) key=value : key should be theproperty as mentioned above, value should be the events’ property value to filter the event |
|  /api/match/deleteevent/<int:match_id> | DELETE    |  It deletes the event with matching match id. Once deleted, event information can’t be retrieved. So careful while using this API   |

## APIs with examples
### /api/match/createevent
It creates the sporting event with the provided information. If PUT method is used to update already created event, it doesn’t update any information i.e. it should be used only to create new event

#### Request 
Request should be send with data in JSON format as per below example:
URI : http://example.com/api/match/createevent
```json
{
   "id":8661032861909884224,
   "message_type":"NewEvent",
   "event":{
      "id":994839351740,
      "name":"Real Madrid vs Barcelona",
      "startTime":"2021-06-20 10:30:00",
      "sport":{
         "id":221,
         "name":"Football"
      },
      "markets":[
         {
            "id":385086549360973392,
            "name":"Winner",
            "selections":[
               {
                  "id":8243901714083343527,
                  "name":"Real Madrid",
                  "odds":1.01
               },
               {
                  "id":5737666888266680774,
                  "name":"Barcelona",
                  "odds":1.01
               }
            ]
         }
      ]
   }
}
```

#### Response
```json
{
'status': 'Created Event'
}
```

#### Response codes
- Normal: 'Created Event' (200)
- Error: 'Provided Information is not correct'(404), 'Unable to create new Event'(500)


### /api/match/updateodds
Updates the odds information of the already created sporting event, all the other fields remain unchanged i.e. though other fields have been changed in request, these are not going to be updated

#### Request 
Request should be send with data in JSON format as per below example:
URI : http://example.com/api/match/updateodds

```json
{
   "id":8661032861909884224,
   "message_type":"UpdateOdds",
   "event":{
      "id":994839351740,
      "name":"Real Madrid vs Barcelona",
      "startTime":"2021-06-20 10:30:00",
      "sport":{
         "id":221,
         "name":"Football"
      },
      "markets":[
         {
            "id":385086549360973392,
            "name":"Winner",
            "selections":[
               {
                  "id":8243901714083343527,
                  "name":"Real Madrid",
                  "odds":10.00
               },
               {
                  "id":5737666888266680774,
                  "name":"Barcelona",
                  "odds":5.55
               }
            ]
         }
      ]
   }
}
```
#### Response
```json
{
'status': 'Updated Odds successfully'
}
```

#### Response codes
- Normal: 'Updated Odds successfully' (200) 

- Error: 'Provided Information is not correct'(404), 'Event not avaialable with provided Id'(404), 'Unable to update Odds'(500)

### /api/match/<int:id>
It provides the event information corresponding to provided match ID, if match id is not correct then returns failure

#### Request 
Request should be send without any data as per below example:
URI : http://example.com/api/match/994839351740

#### Response
```json
{
   "id":994839351740,
   "url":"http://example.com/api/match/994839351740",
   "name":"Real Madrid vs Barcelona",
   "startTime":"2021-06-20 10:30:00",
   "sport":{
      "id":221,
      "name":"Football"
   },
   "markets":[
      {
         "id":385086549360973392,
         "name":"Winner",
         "selections":[
            {
               "id":8243901714083343527,
               "name":"Real Madrid",
               "odds":1.01
            },
            {
               "id":5737666888266680774,
               "name":"Barcelona",
               "odds":1.01
            }
         ]
      }
   ]
}
```
#### Response codes
- Normal: In case of successful response (200) 

- Error: 'Match Id not provided' (404), "Event with Match ID not available" (404)

### /api/match/?<Query Arguments>
It provides the events’ information corresponding to query. Supported queries are 
- ordering=<key> : key should be the properties of event i.e. startTime, id, name

- key=value : key should be property as mentioned above, value should be the events’ property value to filter the event

#### Request 1
Request should be send without any data as per below example:
URI : http://example.com/api/match/?ordering=startTime

#### Response 1
```json
[
   {
      "id":994839351740,
      "url":"http://example.com/api/match/994839351740",
      "name":"Real Madrid vs Barcelona",
      "startTime":"2021-06-20 10:30:00"
   },
   {
      "id":994839351788,
      "url":"http://example.com/api/match/994839351788",
      "name":"Cavaliers vs Lakers",
      "startTime":"2021-01-15 22:00:00"
   }
]
```
#### Request 2
URI : http://example.com/api/match/?ordering=id

#### Response 2
```json
[
   {
      "id":994839351740,
      "url":"http://example.com/api/match/994839351740",
      "name":"Real Madrid vs Barcelona",
      "startTime":"2021-06-20 10:30:00"
   },
   {
      "id":994839351788,
      "url":"http://example.com/api/match/994839351788",
      "name":"Cavaliers vs Lakers",
      "startTime":"2021-01-15 22:00:00"
   }
]
```

#### Request 3
URI : http://example.com/api/match/?name=Real%20Madrid%20vs%20Barcelona
#### Response 3
```json
[
   {
      "id":994839351740,
      "url":"http://example.com/api/match/994839351740",
      "name":"Real Madrid vs Barcelona",
      "startTime":"2021-06-20 10:30:00"
   }
]
```

#### Response codes
- Normal: In case of successful deletion (200) 

- Error: Ordering can't be done with provided information(404), "No information found for query <query information>”(404)

### /api/match/deleteevent/<int:match_id>
It deletes the event with matching match id. Once deleted, event information can’t be retrieved. So careful while using this API.

#### Request 
Request should be send without any data as per below example:
URI : http://example.com/api/match/deleteevent/994839351740

#### Response
```json
{
  "status": "Deleted Event"
}
```
#### Response codes
- Normal: In case of successful deletion (200) 

- Error: 'Match Id not provided' (404)


### Dependencies 
- Make sure that python2.7 is installed

- Below python module shall be available:
  - flask 
  - pymongo 
  - requests 

- Mongo DB should be running in backend


## License
Free
