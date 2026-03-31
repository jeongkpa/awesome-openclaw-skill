#!/usr/bin/env python3
"""Helpers for file-based n8n workflow edit/apply flows.

Typical usage:
1. export a workflow to JSON
2. edit the file locally
3. validate the JSON
4. apply it back with PUT
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    from n8n_api import N8nClient
except ImportError:
    from scripts.n8n_api import N8nClient


READ_ONLY_KEYS = {
    'activeVersion', 'activeVersionId', 'createdAt', 'updatedAt', 'shared',
    'tags', 'versionCounter', 'triggerCount', 'isArchived'
}


def clean_for_update(workflow: dict) -> dict:
    cleaned = dict(workflow)
    for key in READ_ONLY_KEYS:
        cleaned.pop(key, None)
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser(description='Export/apply n8n workflows as files')
    sub = parser.add_subparsers(dest='action', required=True)

    export_p = sub.add_parser('export', help='Export workflow JSON to a file')
    export_p.add_argument('--id', required=True, help='Workflow ID')
    export_p.add_argument('--out', required=True, help='Output JSON file path')
    export_p.add_argument('--exclude-pinned-data', action='store_true', help='Exclude pinned data when exporting')
    export_p.add_argument('--clean', action='store_true', help='Remove read-only fields to make the file update-ready')

    apply_p = sub.add_parser('apply', help='Apply a JSON file to an existing workflow with PUT')
    apply_p.add_argument('--id', required=True, help='Workflow ID')
    apply_p.add_argument('--file', required=True, help='Input JSON file path')
    apply_p.add_argument('--pretty', action='store_true', help='Pretty print output')

    args = parser.parse_args()
    client = N8nClient()

    if args.action == 'export':
        workflow = client.get_workflow(args.id)
        if args.clean:
            workflow = clean_for_update(workflow)
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + '\n')
        print(str(out_path))
        return

    if args.action == 'apply':
        workflow_data = json.loads(Path(args.file).read_text())
        result = client.update_workflow(args.id, workflow_data)
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
