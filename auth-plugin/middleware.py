import urllib
import re

from tyk.decorators import *
from gateway import TykGateway as tyk

REGEX = r"basic|bearer"


@Hook
def MyAuthMiddleware(request, session, metadata, spec):
    auth_header = request.get_header('Authorization')
    api_key = request.object.params.get('api_key')
    tyk.log('Header: {}'.format(str(request.object.headers)), "info")
    tyk.log('Api key: {}'.format(str(api_key)), "info")
    tyk.log(str(dir(request.object)), "info")

    headerAuthSchema = re.search(REGEX, auth_header, re.MULTILINE | re.IGNORECASE)
    
    if not headerAuthSchema and not api_key:
        return request, session, metadata

    metadata['token'] = "47a0c79c427728b3df4af62b9228c8ae"
    # if auth_header == '47a0c79c427728b3df4af62b9228c8ae':
    #     tyk.log("I'm logged!", "info")
    #     tyk.log("Request body" + request.object.body, "info")
    #     tyk.log("API config_data" + spec['config_data'], "info")
    #     session.rate = 1000.0
    #     session.per = 1.0
    #     metadata["token"] = "47a0c79c427728b3df4af62b9228c8ae"
    return request, session, metadata