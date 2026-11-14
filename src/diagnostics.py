"""Network metadata only: exclude headers, bodies, queries and arbitrary text."""
import json
from urllib.parse import urlsplit


def sanitize(entries, kind):
    result = []
    for entry in entries:
        row = {k: entry.get(k) for k in ('level', 'timestamp')}
        if kind == 'performance':
            event = json.loads(entry['message'])['message']
            row['event'] = event.get('method')
            params = event.get('params', {})
            for key in ('request', 'response'):
                obj = params.get(key, {})
                if 'url' in obj:
                    parts = urlsplit(obj['url'])
                    row['origin'] = f'{parts.scheme}://{parts.hostname or ""}'
                for field in ('status', 'method', 'mimeType'):
                    if field in obj:
                        row[field] = obj[field]
            for field in ('encodedDataLength', 'type', 'canceled'):
                if field in params:
                    row[field] = params[field]
        else:
            row['source'] = entry.get('source')
        result.append(row)
    return result
