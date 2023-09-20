# MetaAgent
:robot: A platform to build, manage and deploy your customized digital humans and AI agent. :space_invader: :unicorn: :crystal_ball:



### Minio S3
For sending to frontend, we use Minio S3. More information about Minio S3 can be found : https://min.io/
The service is provided on 192.168.0.20:9000. We use the default access_key and secret_key: "minioadmin:minioadmin". The bucket_name is metaagent.

### Http Service
IP address: http://localhost:60596/default
Header: 'Content-Type: application/json'
Request: {"data": [{"text": "draw a picture of Elon"}]}
Response: {"data": [{"text": "response"}]}