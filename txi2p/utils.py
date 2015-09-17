from twisted.internet.endpoints import clientFromString

from txi2p.helpers import getApi
from txi2p.sam import api as samApi


_apiGenerators = {
    'SAM': samApi.generateDestination,
}

def generateDestination(reactor, keyfile, api=None, apiEndpoint=None):
    api, apiEndpoint = getApi(api, apiEndpoint, _apiGenerators)
    if isinstance(apiEndpoint, str):
        apiEndpoint = clientFromString(reactor, apiEndpoint)
    return _apiGenerators[api](keyfile, apiEndpoint)
