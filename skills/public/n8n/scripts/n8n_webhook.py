#!/usr/bin/env python3
"""Trigger n8n webhook workflows from the CLI.

Use this helper for n8n Cloud/public v1 flows where generic direct workflow
execution is not exposed by the public API. Activate the workflow first, then
call the webhook URL with JSON payload.
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any


def build_webhook_url(base_url: str, path: str, test: bool = False) -> str:
    path = path.lstrip('/')
    prefix = 'webhook-test' if test else 'webhook'
    return f"{base_url.rstrip('/')}/{prefix}/{path}"


def trigger_webhook(base_url: str, path: str, data: Optional[Dict[str, Any]] = None,
                    method: str = 'POST', test: bool = False, timeout: int = 30) -> Dict[str, Any]:
    url = build_webhook_url(base_url, path, test=test)
    response = requests.request(
        method.upper(),
        url,
        json=data if data is not None else {},
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
        timeout=timeout,
    )

    result = {
        'url': url,
        'status_code': response.status_code,
        'ok': response.ok,
        'headers': dict(response.headers),
    }

    try:
        result['body'] = response.json()
    except Exception:
        result['body'] = response.text

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description='Trigger an n8n webhook URL')
    parser.add_argument('--path', required=True, help='Webhook path, e.g. my-flow')
    parser.add_argument('--base-url', default=os.getenv('N8N_BASE_URL'), help='n8n base URL (defaults to N8N_BASE_URL)')
    parser.add_argument('--data', help='Inline JSON payload')
    parser.add_argument('--data-file', help='Path to JSON payload file')
    parser.add_argument('--method', default='POST', help='HTTP method (default: POST)')
    parser.add_argument('--test', action='store_true', help='Call /webhook-test/... instead of /webhook/...')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout seconds')
    parser.add_argument('--pretty', action='store_true', help='Pretty print output')
    args = parser.parse_args()

    if not args.base_url:
        raise ValueError('N8N_BASE_URL not found in environment and --base-url not provided')

    payload = None
    if args.data_file:
        with open(args.data_file, 'r') as f:
            payload = json.load(f)
    elif args.data:
        payload = json.loads(args.data)

    result = trigger_webhook(
        base_url=args.base_url,
        path=args.path,
        data=payload,
        method=args.method,
        test=args.test,
        timeout=args.timeout,
    )

    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))

    if not result['ok']:
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
