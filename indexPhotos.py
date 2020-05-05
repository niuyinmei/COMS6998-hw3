import json
import boto3
import datetime
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

// commented just now
rekogclient = boto3.client('rekognition')

region = 'us-east-1'
service = 'es'
host = 'vpc-photos-yjqveupd7eewpglvr45tohwkpa.us-east-1.es.amazonaws.com'

credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
esclient = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    request_timeout=1000
)





def lambda_handler(event, context):
    # read labels from Rekognition
    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    img = event["Records"][0]["s3"]["object"]
    img_labels_obj = rekogclient.detect_labels(
        Image={
            'S3Object': {
                'Bucket': s3_bucket,
                'Name': img["key"]
            }
        }
    )
    img_labels = [label["Name"].lower() for label in img_labels_obj["Labels"]]
    # save image and labels to ES
    img_obj = {
        "objectKey": img["key"],
        "bucket": s3_bucket,
        "createdTimestamp": str(datetime.datetime.now()),
        "labels": img_labels
    }
    print(json.dumps(img_obj))
    
#  ----------------------------------------------------------------------------------------------------
    # awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    # print("awsauth: "+str(awsauth))
    # index = 'photos'
    # type = 'lambda-type'
    # url = 'https://' + host + '/' + index + '/' + type
    # headers = { "Content-Type": "application/json" }
    # print ("here")
    # print (url)
    
    # r = json.loads(requests.delete(url, auth=awsauth, headers=headers, data=json.dumps(query)).text)
    # r = requests.delete(url, auth=awsauth, json=img_obj, headers=headers)
    # print (r)
    # print (r.text)

#----------------------------------------------------------------------------------
    retval = esclient.index(index="photos", doc_type="_doc", body=img_obj, id=img["key"].replace(".", "-"))
    print(retval)

    # query = {
    #     "query" :{
    #         "match" : {
    #             "bucket" :s3_bucket
    #         }
    #     }
    # }
    # delete_by_query
    # print(esclient.count(
    #     index="photos", doc_type="_doc", body=query
    # ))
    temp = {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
