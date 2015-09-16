DEFAULT_ENDPOINT = {
    'BOB': 'tcp:127.0.0.1:2827',
    'SAM': 'tcp:127.0.0.1:7656',
    }

DEFAULT_API = 'BOB'


def getApi(api, apiEndpoint, apiDict):
    if not api:
        if apiEndpoint:
            raise ValueError('api must be specified if apiEndpoint is given')
        else:
            api = DEFAULT_API

    if api not in apiDict:
        raise ValueError('Specified I2P API is invalid or unsupported')

    if not apiEndpoint:
        apiEndpoint = DEFAULT_ENDPOINT[api]

    return (api, apiEndpoint)
