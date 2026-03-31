#!/usr/bin/env python3
"""Execution helpers for n8n.

Provides concise listing/filtering and detail views for executions.
"""

import sys
import json
import argparse

try:
    from n8n_api import N8nClient
except ImportError:
    from scripts.n8n_api import N8nClient


def summarize(execution: dict) -> dict:
    return {
        'id': execution.get('id'),
        'workflowId': execution.get('workflowId'),
        'status': execution.get('status'),
        'mode': execution.get('mode'),
        'finished': execution.get('finished'),
        'startedAt': execution.get('startedAt'),
        'stoppedAt': execution.get('stoppedAt'),
        'retryOf': execution.get('retryOf'),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='n8n execution helper')
    sub = parser.add_subparsers(dest='action', required=True)

    recent_p = sub.add_parser('recent', help='List recent execution summaries')
    recent_p.add_argument('--workflow-id', help='Filter by workflow ID')
    recent_p.add_argument('--limit', type=int, default=10)
    recent_p.add_argument('--status', help='Filter summary rows by status')
    recent_p.add_argument('--pretty', action='store_true')

    show_p = sub.add_parser('show', help='Show one execution in detail')
    show_p.add_argument('--id', required=True, help='Execution ID')
    show_p.add_argument('--pretty', action='store_true')

    args = parser.parse_args()
    client = N8nClient()

    if args.action == 'recent':
        rows = client.list_executions(workflow_id=args.workflow_id, limit=args.limit)
        data = rows.get('data', rows) if isinstance(rows, dict) else rows
        items = [summarize(x) for x in data]
        if args.status:
            items = [x for x in items if x.get('status') == args.status]
        if args.pretty:
            print(json.dumps(items, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(items, ensure_ascii=False))
        return

    if args.action == 'show':
        result = client.get_execution(args.id)
        if args.pretty:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False))
        return


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
