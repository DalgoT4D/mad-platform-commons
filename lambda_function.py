import os
import urllib3
import base64
from urllib.parse import urlencode

http = urllib3.PoolManager()
API_BASE_URL = os.environ.get("API_BASE_URL", "https://your.api.com")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

def lambda_handler(event, context):
    if LOG_LEVEL in ["DEBUG"]:
        print(event)

    method = event["requestContext"]['http']['method']
    path = event["requestContext"]['http']['path']
    headers = event.get('headers') or {}

    if LOG_LEVEL in ["DEBUG"]:
        print(path)

    # Prepare query parameters
    raw_query = event.get('queryStringParameters') or {}
    query = dict(raw_query)

    school_ids_path = '/gateway/commons-report-service/api/v2/datasets/name/PS3_MAD_SCHOOL_IDS/execute'

    if path == school_ids_path and 'page' not in query:
        query['page'] = '0'

    query_string = urlencode(query, doseq=True)

    url = f"{API_BASE_URL}{path}"
    if query_string:
        url += f"?{query_string}"

    if LOG_LEVEL in ["INFO", "DEBUG"]:
        print(url)

    # Prepare body
    body = event.get('body')
    if event.get('isBase64Encoded', False) and body is not None:
        body = base64.b64decode(body)
    elif body is not None:
        body = body.encode()

    # Remove headers that urllib3 should not forward
    headers.pop('Host', None)
    
    # Send request
    response = http.request(
        method,
        url,
        body=body,
        headers=headers,
        preload_content=False
    )
    if LOG_LEVEL in ["DEBUG"]:
        print(response.headers)

    body_bytes = response.read(decode_content=False)
    response.release_conn()

    encoded_body = base64.b64encode(body_bytes).decode('utf-8')

    return {
        "statusCode": response.status,
        "headers": dict(response.headers),
        "body": encoded_body,
        "isBase64Encoded": True,
    }
