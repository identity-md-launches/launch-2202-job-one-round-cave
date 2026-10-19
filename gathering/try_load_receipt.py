#!/usr/bin/env python3
"""Review actual local tool-execution journal under two asserted clock models."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('gathering_load_receipt',
    ROOT / 'shared/load-receipt/load_receipt.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


def now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')


def main():
    commands = [('cluster-verdict', ['line-1/tools/cluster-verdict/cluster_verdict.py', '--demo']),
                ('bidi-scope', ['line-2/tools/bidi-scope/bidi_scope.py', '--demo']),
                ('timeline-load', ['line-3/tools/timeline-load/timeline_load.py', 'demo']),
                ('worksheet-receipt', ['line-4/tools/worksheet-receipt/worksheet_receipt.py', 'demo'])]
    lines, executions = [], []
    start = now()
    for name, arguments in commands:
        began = now()
        run = subprocess.run([sys.executable, '-B', *arguments], cwd=ROOT,
                             capture_output=True, timeout=30)
        ended = now()
        if run.returncode != 0:
            raise ValueError(f'{name} failed: exit {run.returncode}')
        lines.extend([f'{began} {name} start\n', f'{ended} {name} exit=0\n'])
        executions.append({'tool': name, 'command': ['python3', '-B', *arguments],
                           'start': began, 'end': ended, 'exit_code': run.returncode,
                           'stdout_sha256': app.hashlib.sha256(run.stdout).hexdigest()})
    end = now()
    raw = ''.join(lines).encode('ascii')
    window = app.load.instant(end) - app.load.instant(start)
    observations = []
    for clock_ms in (0, 750):
        request = {'pack': app.load.replay.make_pack([('observed-local-cli.log', raw)],
                                                    clock_uncertainty_ms=clock_ms),
                   'start': start, 'end': end, 'max_uncovered': app.seconds(window),
                   'max_mean_depth': '8'}
        receipt = app.create(request)
        observations.append({'asserted_clock_uncertainty_ms': clock_ms,
                             'receipt': receipt,
                             'replay': app.verify(receipt, receipt['receipt_sha256'])})
    print(json.dumps({'data_kind': 'observed_local_process_journal',
        'executions': executions, 'observations': observations,
        'limitations': 'Actual local process observation timestamps, not an external service incident. '
        'Tool demo payloads are synthetic. Clock accuracy is unmeasured; 750 ms is illustrative. '
        'Budgets allow the whole window uncovered and at most eight compatible intervals on average; '
        'they are post hoc examples, not SLOs. Coverage and mean depth do not measure runtime, '
        'downtime, confirmed concurrency or service load.'}, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
