#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib import request, parse, error


def load_local_env() -> None:
    candidates = [
        Path.cwd() / '.env',
        Path.home() / '.openclaw' / 'skills' / 'n8n' / '.env',
    ]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


class N8nSafeClient:
    def __init__(self):
        load_local_env()
        self.base_url = (os.getenv('N8N_API_URL') or os.getenv('N8N_BASE_URL') or '').rstrip('/')
        self.api_key = os.getenv('N8N_API_KEY')
        if not self.base_url:
            raise ValueError('N8N_API_URL or N8N_BASE_URL not found')
        if not self.api_key:
            raise ValueError('N8N_API_KEY not found')
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def _request(self, method: str, endpoint: str, params=None, body=None, retries: int = 0):
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        if params:
            url = f"{url}?{parse.urlencode(params)}"
        data = None if body is None else json.dumps(body).encode('utf-8')
        req = request.Request(url, data=data, headers=self.headers, method=method)
        backoffs = [3, 10, 25]
        attempt = 0
        while True:
            try:
                with request.urlopen(req, timeout=60) as resp:
                    content = resp.read()
                    return json.loads(content.decode('utf-8')) if content else {}
            except error.HTTPError as e:
                error_body = e.read().decode('utf-8', errors='replace')
                transient = e.code >= 500
                if transient and attempt < retries:
                    time.sleep(backoffs[min(attempt, len(backoffs) - 1)])
                    attempt += 1
                    continue
                raise RuntimeError(f'HTTP {e.code}: {error_body}') from e
            except error.URLError as e:
                if attempt < retries:
                    time.sleep(backoffs[min(attempt, len(backoffs) - 1)])
                    attempt += 1
                    continue
                raise RuntimeError(f'Connection error: {e.reason}') from e

    def list_workflows(self, limit: int = 20):
        return self._request('GET', 'workflows', params={'limit': limit}, retries=1)

    def get_workflow(self, workflow_id: str):
        return self._request('GET', f'workflows/{workflow_id}', retries=1)

    def create_workflow(self, workflow: dict):
        clean = dict(workflow)
        for key in ['id', 'active', 'versionId', 'createdAt', 'updatedAt']:
            clean.pop(key, None)
        return self._request('POST', 'workflows', body=clean, retries=1)

    def update_workflow(self, workflow_id: str, workflow: dict):
        try:
            return self._request('PATCH', f'workflows/{workflow_id}', body=workflow, retries=1)
        except RuntimeError as e:
            if '405' not in str(e):
                raise
        return self._request('PUT', f'workflows/{workflow_id}', body=workflow, retries=1)

    def activate_workflow(self, workflow_id: str):
        try:
            return self._request('POST', f'workflows/{workflow_id}/activate', retries=1)
        except RuntimeError:
            return self._request('PATCH', f'workflows/{workflow_id}', body={'active': True}, retries=1)

    def deactivate_workflow(self, workflow_id: str):
        try:
            return self._request('POST', f'workflows/{workflow_id}/deactivate', retries=1)
        except RuntimeError:
            return self._request('PATCH', f'workflows/{workflow_id}', body={'active': False}, retries=1)


def load_json(path: str):
    with open(path, 'r') as f:
        return json.load(f)


def summarize(obj):
    if isinstance(obj, dict):
        keys = ['id', 'name', 'active', 'isArchived', 'versionId', 'updatedAt', 'createdAt']
        return {k: obj.get(k) for k in keys if k in obj}
    return obj


def main():
    parser = argparse.ArgumentParser(description='Safe n8n operations with retries and method fallbacks')
    parser.add_argument('action', choices=['list', 'get', 'create', 'update', 'activate', 'deactivate'])
    parser.add_argument('--id', help='Workflow ID')
    parser.add_argument('--file', help='Workflow JSON file')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    client = N8nSafeClient()
    if args.action == 'list':
        result = client.list_workflows(limit=args.limit)
    elif args.action == 'get':
        if not args.id:
            raise SystemExit('--id required')
        result = client.get_workflow(args.id)
    elif args.action == 'create':
        if not args.file:
            raise SystemExit('--file required')
        result = client.create_workflow(load_json(args.file))
    elif args.action == 'update':
        if not args.id or not args.file:
            raise SystemExit('--id and --file required')
        result = client.update_workflow(args.id, load_json(args.file))
    elif args.action == 'activate':
        if not args.id:
            raise SystemExit('--id required')
        result = client.activate_workflow(args.id)
    elif args.action == 'deactivate':
        if not args.id:
            raise SystemExit('--id required')
        result = client.deactivate_workflow(args.id)
    print(json.dumps(result if args.action in ['list', 'get'] else summarize(result), indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
