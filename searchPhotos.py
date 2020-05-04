import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


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
    print(event)
    # send keys to lex
    lex_rsp = client.post_text(
        botName=' photoBot',
        botAlias='searchEngine',
        userId='njkhvgcfxrteyu',
        inputText="dog"# currently hard code, should use event[""]
    )
    print(lex_rsp)
    
    keys = event["slots"]
    labels = [value for value in keys.values() if value != "None"]
    # search in ES
    query_body = {
        "query": {
            "match": {"labels": " ".join(labels)}
        }
    }
    print(query_body)
    result = esclient.search(index="photos", body=query_body)
    print("rsp: ", rsp)
    # rsp:  {'took': 68, 'timed_out': False, '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0}, 'hits': {'total': {'value': 3, 'relation': 'eq'}, 'max_score': 0.2876821, 'hits': [{'_index': 'photos', '_type': 'lambda-type', '_id': 'qMG5zHEB_oaWeBid_Dfw', '_score': 0.2876821, '_source': {'objectKey': 'dogs.jpg', 'bucket': 'photosphotosb2b2', 'createdTimestamp': '2020-04-30 20:14:32.907093', 'labels': ['Animal', 'Mammal', 'Dog', 'Labrador Retriever', 'Pet', 'Canine', 'Golden Retriever']}}, {'_index': 'photos', '_type': 'lambda-type', '_id': 'dogs-jpg', '_score': 0.2876821, '_source': {'objectKey': 'dogs.jpg', 'bucket': 'photosphotosb2b2', 'createdTimestamp': '2020-04-30 21:02:05.549017', 'labels': ['Pet', 'Canine', 'Animal', 'Mammal', 'Labrador Retriever', 'Dog', 'Golden Retriever']}}, {'_index': 'photos', '_type': 'lambda-type', '_id': 'p8GjzHEB_oaWeBidXzda', '_score': 0.2876821, '_source': {'objectKey': 'dogs.jpg', 'bucket': 'photosphotosb2b2', 'createdTimestamp': '2020-04-30 19:49:50.600147', 'labels': ['Canine', 'Animal', 'Pet', 'Dog', 'Mammal', 'Labrador Retriever', 'Golden Retriever']}}]}}
    # respound to frontend
    rsp = dict()
    rsp["results"] = []
    for item in result["hits"]["hits"]:
        img_id = item["_source"]["objectKey"]
        img_bucket = item["_source"]["bucket"]
        img_url = "https://" + img_bucket +".s3.amazonaws.com/" + img_id
        rsp["results"].append(img_url)
    print(rsp)
    
    return {
        'statusCode': 200,
        'body': rsp
    }

