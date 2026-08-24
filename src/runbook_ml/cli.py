import argparse
import json

from .store import ExperimentStore


def main(argv=None):
    parser = argparse.ArgumentParser(prog='runbook')
    parser.add_argument('--db', default='artifacts/runbook.sqlite3')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    compare = sub.add_parser('compare')
    compare.add_argument('--metric', default='accuracy')
    promote = sub.add_parser('promote')
    promote.add_argument('run_id', type=int)
    promote.add_argument('--metric', required=True)
    promote.add_argument('--minimum', type=float, required=True)
    args = parser.parse_args(argv)
    store = ExperimentStore(args.db)

    if args.command == 'list':
        print(json.dumps(store.list_runs(), indent=2))
        return 0
    if args.command == 'compare':
        print(json.dumps(store.compare(args.metric), indent=2))
        return 0
    try:
        print(json.dumps(store.promote(args.run_id, args.metric, args.minimum), indent=2))
        return 0
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    raise SystemExit(main())
