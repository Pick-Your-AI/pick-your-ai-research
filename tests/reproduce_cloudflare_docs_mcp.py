"""Dated, credential-free probe of Cloudflare's public documentation MCP only."""
import argparse
import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
from importlib.metadata import version
import json
import sys

HOST = 'https://docs.mcp.cloudflare.com'
QUERY = 'How does Streamable HTTP differ from the deprecated HTTP+SSE transport for MCP?'


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def model(value):
    return value.model_dump(mode='json', by_alias=True, exclude_none=True)


async def observe(generation, route, mode, search):
    expected = {'v1': '1.30.0', 'v2': '2.3.0'}[generation]
    if version('mcp') != expected or (generation == 'v2' and version('mcp-types') != '2.3.0'):
        raise ValueError('The interpreter must use the exact previously recorded SDK environment')
    if generation == 'v1' and mode != 'legacy':
        raise ValueError('SDK v1 only has the legacy initialization path')
    if generation == 'v1':
        import httpx as http
    else:
        import httpx2 as http
    from mcp.client.streamable_http import streamable_http_client

    endpoint = HOST + '/' + route
    row = {'observed_at': datetime.now(timezone.utc).isoformat(),
           'client_sdk': expected, 'mode': mode, 'endpoint': endpoint,
           'transport': 'streamable_http', 'status': 'failed', 'http_requests': []}

    async def before(request):
        if str(request.url) != endpoint or request.method not in ('GET', 'POST'):
            raise ValueError('Request left the fixed public documentation endpoint or method scope')
        if any(name in request.headers for name in ('authorization', 'cookie', 'proxy-authorization')):
            raise ValueError('Credentials are outside this public documentation probe')
        item = {'method': request.method, 'url': str(request.url), 'credential_headers': False}
        if request.method == 'POST':
            message = json.loads(request.content)
            method = message.get('method')
            if method not in ('initialize', 'notifications/initialized', 'server/discover', 'tools/list', 'tools/call'):
                raise ValueError('Unexpected MCP operation')
            if method == 'tools/call' and message.get('params', {}).get('name') != 'search_cloudflare_documentation':
                raise ValueError('Only the source-inspected documentation search may be called')
            if method == 'tools/call' and message.get('params', {}).get('arguments') != {'query': QUERY}:
                raise ValueError('Only the fixed public documentation query may be submitted')
            item.update(rpc_method=method, request=digest(message))
        row['http_requests'].append(item)

    async def after(response):
        row.setdefault('http_responses', []).append({
            'status': response.status_code, 'method': response.request.method,
            'url': str(response.request.url),
            'content_type': response.headers.get('content-type'),
            'protocol_header': response.headers.get('mcp-protocol-version'),
            'session_header_present': 'mcp-session-id' in response.headers,
        })

    async def operations(client):
        listing = await client.list_tools()
        dumped = model(listing)
        row['tools'] = [{'name': tool['name'],
                         'read_only_hint': tool.get('annotations', {}).get('readOnlyHint'),
                         'input_schema': digest(tool.get('inputSchema'))}
                        for tool in dumped['tools']]
        row['next_cursor'] = dumped.get('nextCursor')
        row['listing'] = digest(dumped)
        if search:
            selected = [tool for tool in row['tools'] if tool['name'] == 'search_cloudflare_documentation']
            if len(selected) != 1 or selected[0]['read_only_hint'] is not True:
                raise ValueError('The source-inspected read-only search is not in the observed tool list')
            result = model(await client.call_tool('search_cloudflare_documentation', {'query': QUERY}))
            row['search'] = {'query': QUERY, 'is_error': result.get('isError'), 'result': digest(result)}
            structured = result.get('structuredContent')
            if isinstance(structured, dict) and isinstance(structured.get('results'), list):
                row['search']['result_count'] = len(structured['results'])
                row['search']['urls'] = [item.get('url') for item in structured['results']]
            if result.get('isError') is not False:
                raise ValueError('Documentation search did not return an explicit successful tool result')

    try:
        async with http.AsyncClient(timeout=15, follow_redirects=False,
                                    event_hooks={'request': [before], 'response': [after]}) as http_client:
            transport = streamable_http_client(endpoint, http_client=http_client, terminate_on_close=False)
            if generation == 'v1':
                from mcp import ClientSession
                async with transport as (read, write, get_session_id):
                    async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=15)) as client:
                        initialized = await client.initialize()
                        row['server_info'] = model(initialized.serverInfo)
                        row['protocol_version'] = initialized.protocolVersion
                        await operations(client)
                        row['session_id_present'] = get_session_id() is not None
            else:
                from mcp import Client
                async with Client(transport, mode=mode, read_timeout_seconds=15) as client:
                    await operations(client)
                    row['protocol_version'] = client.protocol_version
                    row['server_info'] = model(client.server_info) if client.server_info is not None else None
        row['status'] = 'passed'
    except Exception as error:
        def errors(exc):
            if isinstance(exc, BaseExceptionGroup):
                return [item for child in exc.exceptions for item in errors(child)]
            return [{'type': type(exc).__name__, 'message': str(exc)[:500]}]
        row['errors'] = errors(error)
    return row


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generation', choices=('v1', 'v2'), required=True)
    parser.add_argument('--route', choices=('mcp', 'sse'), default='mcp')
    parser.add_argument('--mode', choices=('legacy', 'auto', '2026-07-28'), required=True)
    parser.add_argument('--search', action='store_true')
    args = parser.parse_args()
    observation = asyncio.run(observe(args.generation, args.route, args.mode, args.search))
    observation['script_sha256'] = hashlib.sha256(open(__file__, 'rb').read()).hexdigest()
    print(json.dumps(observation, indent=2, sort_keys=True))
    sys.exit(0 if observation['status'] == 'passed' else 1)
