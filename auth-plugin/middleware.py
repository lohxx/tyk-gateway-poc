import re
import json
import http.client as client

from tyk.decorators import *
from gateway import TykGateway as tyk

REGEX = r"basic|bearer"


@Hook
def MyAuthMiddleware(request, session, metadata, spec):
    auth_header = request.get_header('Authorization') or ''
    api_key = request.object.params.get('api_key')

    headerAuthSchema = re.search(REGEX, auth_header, re.MULTILINE | re.IGNORECASE)
    if not headerAuthSchema and not api_key:
        return request, session, metadata

    key = None
    if headerAuthSchema:
        key = re.sub(REGEX, '', auth_header, 1, re.MULTILINE | re.IGNORECASE)
    elif api_key:
        key = api_key
    
    tyk.log(f'api key: {api_key} - {key}', "info")
    conn = client.HTTPConnection("localhost", 8080)
    conn.request(method='GET', url=f'http://localhost:8080/tyk/keys/{key.strip()}', headers={'x-tyk-authorization': 'foo'})
    response = conn.getresponse()

    if response.status != 200:
        return request, session, metadata

    user_data = json.loads(response.read())
    tyk.log(str(user_data), "info")
    metadata['token'] = key
    # definir a session das quotas e rate limit aqui..

    return request, session, metadata