import click
import json
import requests
import concurrent
from concurrent.futures import ThreadPoolExecutor

@click.group()
def cli():
    pass

def doCalls(key):
    response = requests.get(
        'http://127.0.0.1:8080/test/',
        headers={'Authorization': f'Bearer {key}'})

    return response

@cli.command()
def callsRateLimit():
    with ThreadPoolExecutor(max_workers=30) as executor:
        future_to_url = []
        for _ in range(170):
            future_to_url.append(executor.submit(doCalls, '15f48e1b975284942a02e7c94eba27159'))

        for future in concurrent.futures.as_completed(future_to_url):
            try:
                response = future.result()
            except Exception as e:
                print(e)

        print(response.json())
        assert response.status_code == 429
        response.json()['error'] == 'Rate limit exceeded'

@cli.command()
def callsQuota():
    for _ in range(110):
        response = doCalls('1caf9578da40e41bbb20cc34895932f56')

    print(response.json())
    assert response.status_code == 403
    assert response.json()['error'] == 'Quota exceeded'

@cli.command()
def setupApi():
    apis = {
        'test': {
            '1caf9578da40e41bbb20cc34895932f56': {
                "rate": 150,
                "allowance": 150,
                "per": 1,
                "quota_max": 100,
                "quota_remaining": -1,

            },
            '15f48e1b975284942a02e7c94eba27159': {
                "rate": 1,
                "allowance": 1,
                "per": 1,
                "quota_max": 170,
                "quota_remaining": -1,
            }
        }
    }

    for api in apis:
        use_keyless = True if apis[api] else False
        response = requests.post(
            'http://localhost:8080/tyk/apis',
            data=json.dumps({
                "name": api,
                "slug": api,
                "api_id": api,
                "org_id": "1",
                "use_keyless": use_keyless,
                "auth": {
                    "auth_header_name": "authorization",
                    "use_param": True,
                    "param_name": "api_key",
                    "use_cookie": False,
                    "cookie_name": ""
                },
                "definition": {
                    "location": "header",
                    "key": "x-api-version"
                },
                "version_data": {
                    "not_versioned": True,
                    "versions": {
                        "Default": {
                            "name": "Default",
                            "use_extended_paths": True
                        }
                    }
                },
                "proxy": {
                    "listen_path": "/test/",
                    "target_url": "http://api:8000/",
                    "strip_listen_path": True
                },
                "active": True,
                "custom_middleware_bundle": "bundle.zip",
                "enable_coprocess_auth": True
            }),
            headers={'x-tyk-authorization': 'foo', 'Content-Type': 'application/json'}
        )

        if response.status_code != 200:
            continue

        for userKey in apis[api]:
            attr = apis[api][userKey]
            response = requests.post(
                f'http://localhost:8080/tyk/keys/{userKey}',
                data=json.dumps({
                    "allowance": attr['allowance'],
                    "rate": attr['rate'],
                    "per": attr['per'],
                    "expires": -1,
                    "quota_max": attr['quota_max'],
                    "org_id": "1",
                    "quota_renews": 1449051461,
                    "quota_remaining": attr['quota_remaining'],
                    "quota_renewal_rate": 60,
                    "access_rights": {
                        api: {
                            "api_id": api,
                            "api_name": api,
                            "versions": ["Default"]
                        }
                    },
                    "meta_data": {}
                }),
                headers={'x-tyk-authorization': 'foo', 'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                print(f'usuário criado, chave: {userKey}')

if __name__ == '__main__':
    cli()