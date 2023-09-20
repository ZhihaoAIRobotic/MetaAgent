# MetaAgent
:unicorn:A platform to build, manage and deploy your customized digital humans  and AI agent:robot:. 

## Installation
#### 1. 

#### 2. Minio S3

## Deployment
we use Minio S3 for sending multi-modal messages to frontend. More information about Minio S3 can be found : https://min.io/. 

The service is provided on 192.168.0.20:9000. We use the default access_key and secret_key: "minioadmin:minioadmin". The bucket_name is metaagent.

### Http Service
IP address:
```
 http://localhost:60596/default
```

Header: 
```
'Content-Type: application/json'
```

Request: 
```
{"data": [{"text": "draw a picture of Elon"}]}
```

Response: 
```
{"data":[{"id":"id_number","text":[{"id":"id_number","text":"url","bytes_":null,"embedding":null,"url":null}],"image":[{"id":"id_number","text":"url","bytes_":null,"embedding":null,"url":null}],"video":[{"id":"id_number","text":"url","bytes_":null,"embedding":null,"url":null}],"audio":[{"id":"id_number","text":"url","bytes_":null,"embedding":null,"url":null}]}],"parameters":{}}
```
