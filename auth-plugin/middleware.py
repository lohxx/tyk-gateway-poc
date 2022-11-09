import re
import json
import http.client as client

from tyk.decorators import *
from gateway import TykGateway as tyk

REGEX = r"basic|bearer"

def setQuotas(user_data, session):
    session.quota_max = user_data['quota_max']
    session.quota_remaining = user_data['quota_remaining']
    session.quota_renewal_rate = user_data['quota_renewal_rate']


def setRateLimit(user_data, session):
    session.allowance = user_data['allowance']
    session.rate = user_data['rate']
    session.per = user_data['per']


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
    conn.request(
        method='GET',
        headers={'x-tyk-authorization': 'foo'},
        url=f'http://localhost:8080/tyk/keys/{key.strip()}')
    response = conn.getresponse()

    if response.status != 200:
        return request, session, metadata

    user_data = json.loads(response.read())
    tyk.log(str(user_data), "info")
    metadata['token'] = key
    setQuotas(user_data, session)
    setRateLimit(user_data, session)

    return request, session, metadata