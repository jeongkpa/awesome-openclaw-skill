#!/usr/bin/env python3
import argparse
import json
import sys
from urllib import request, error


def main():
    parser = argparse.ArgumentParser(description='Basic webhook smoke test for n8n workflows')
    parser.add_argument('url')
    parser.add_argument('--expect-status', type=int, default=200)
    parser.add_argument('--expect-content-type', default='')
    parser.add_argument('--preview-chars', type=int, default=240)
    args = parser.parse_args()
    req = request.Request(args.url, headers={'User-Agent': 'OpenClaw webhook smoke test'})
    try:
        with request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            content_type = resp.headers.get('Content-Type', '')
            ok = resp.status == args.expect_status and (not args.expect_content_type or args.expect_content_type in content_type)
            print(json.dumps({
                'ok': ok,
                'status': resp.status,
                'contentType': content_type,
                'bodyPreview': body[:args.preview_chars]
            }, ensure_ascii=False, indent=2))
            if not ok:
                sys.exit(2)
    except error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(json.dumps({'ok': False, 'status': e.code, 'error': body[:args.preview_chars]}, ensure_ascii=False, indent=2))
        sys.exit(2)


if __name__ == '__main__':
    main()
