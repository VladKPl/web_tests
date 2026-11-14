import json
from src.diagnostics import sanitize


def test_network_diagnostics_exclude_sensitive_fields():
    event = {'message': {'method': 'Network.requestWillBeSent', 'params': {
        'request': {'url': 'https://shop.example/account?password=secret',
                    'method': 'POST', 'headers': {'Authorization': 'secret'},
                    'postData': 'password=secret'}}}}
    result = sanitize([{'message': json.dumps(event), 'timestamp': 1, 'level': 'INFO'}], 'performance')
    serialized = json.dumps(result)
    assert 'secret' not in serialized
    assert 'account' not in serialized
    assert result[0]['origin'] == 'https://shop.example'
    assert result[0]['method'] == 'POST'
