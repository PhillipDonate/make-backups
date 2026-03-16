from isodate import Duration, isoerror
from statemachine import StateMachine, State
from pathlib import Path
from datetime import date, datetime, timedelta
from rich.text import Text
import isodate
import shutil
import Log
import Run

_zipper = Run.get_exe_dir() / '7za.exe'

class ArchiveMachineError(Exception):
    pass

def _parse_iso_duration(s: str) -> Duration:
    try:
        return isodate.parse_duration(s, as_timedelta_if_possible=False)
    except isoerror.ISO8601Error:
        return None

def _get_files_older_than(paths, duration: Duration):
    today = date.today()
    cutoff = today - duration
    deletions = []

    for p in paths:
        try:
            _, datestr = p.stem.rsplit('_', 1)
            file_date = datetime.strptime(datestr, '%Y-%m-%d').date()
        except Exception:
            continue

        if file_date < cutoff:
            deletions.append(p)

    return deletions

def _get_size_text(path: Path):
    size = path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            size = f'{size:.2f} {unit}'
            break
        size /= 1024
    style = 'dim italic grey50'
    text = Text('  ', style=style)
    return text.append(Text(size, style=style))

def _is_at_least_one_day(d: Duration):
    today = date.today()
    future = today + d
    return (future - today) >= timedelta(days=1)

class ArchiveMachine(StateMachine):
    start = State(initial=True)
    packing = State()
    running = State()
    finished = State(final=True)

    # Transitions
    next = start.to(packing) | packing.to(running) | running.to(running)
    complete = running.to(finished) | packing.to(finished)

    failed = False

    def __init__(self, name, steps):
        super().__init__()
        self.name = name
        self.steps = steps
        self.index = 0

    def is_finished(self):
        return self.finished.is_active

    def is_failed(self):
        return self.failed

    def fail(self, e: ArchiveMachineError):
        self.failed = True
        message = str(e)
        message and Log.fail(message)
        self.complete()

    def on_enter_packing(self):
        step = self.steps[self.index]
        self.index += 1
        op = step.get('op')

        try:
            match op:
                case 'pass':
                    self.complete()
                case 'pack':
                    self.op_pack(step)
                case _:
                    raise ArchiveMachineError(f'{self.name}: First step must be pack')

        except ArchiveMachineError as e:
            self.fail(e)

    def on_enter_running(self):
        if self.index >= len(self.steps):
            self.complete()
            return

        step = self.steps[self.index]
        self.index += 1
        op = step.get('op')

        try:
            match op:
                case 'pass':
                    self.complete()
                case 'move':
                    self.op_move(step)
                case 'test':
                    self.op_test(step)
                case 'cull':
                    self.op_cull(step)
                case 'pack':
                    raise ArchiveMachineError(f'{self.name}: Cannot pack again')
                case _:
                    raise ArchiveMachineError(f'{self.name}: Unknown op: {op}')

        except ArchiveMachineError as e:
            self.fail(e)

    def op_pack(self, step):
        zip = step.get('zip') or 'zip'
        src = step['in']
        out = step['out']
    
        if not _zipper.exists():
            raise ArchiveMachineError(f'Not found: {_zipper}')

        source = Path(src)
        target = Path(out)

        if not source.exists():
            raise ArchiveMachineError(f'Not found: {source}')

        if not target.exists():
            raise ArchiveMachineError(f'Not found: {target}')

        today = date.today().strftime('%Y-%m-%d')
        self.filename = self.name + f'_{today}.{zip}'
        self.filepath = target / self.filename

        if self.filepath.is_file():
            self.filepath.unlink()

        message = Text(f'Pack: {self.filename}')
        code = 0

        with Log.status(message):
            cmd = [ _zipper, 'a', '-mx9', self.filepath, source ]
            code = Run.run(cmd)

        if code > 0:
            raise ArchiveMachineError(message)

        message.append(_get_size_text(self.filepath))
        Log.ok(message)

    def op_move(self, step):
        to = step['to']
        target = Path(to)

        if not target.exists():
            raise ArchiveMachineError(f'Not found: {target}')
        
        if not target.is_dir():
            raise ArchiveMachineError(f'Not a directory: {target}')
        
        message = Text(f'Move: {self.filename} -> {target}')
        message.append(_get_size_text(self.filepath))
        
        with Log.status(message):
            try:
                self.filepath = Path(shutil.move(self.filepath, target / self.filename))

            except OSError as e:
                message.append(' ').append(e.strerror)
                raise ArchiveMachineError(message)

            except Exception:
                raise ArchiveMachineError(message)
        
        Log.ok(message)

    def get_all_dates_pattern(self):
        return f'{self.name}_????-??-??{self.filepath.suffix}'
    
    def get_siblings_glob(self, pattern):
        return self.filepath.parent.glob(pattern)

    def op_test(self, step):
        if not _zipper.exists():
            raise ArchiveMachineError(f'Not found: {_zipper}')
    
        pattern = None

        if step.get('all_dates'):
            pattern = self.get_all_dates_pattern()
        else:
            pattern = step.get('pattern') or self.filename

        filepaths = self.get_siblings_glob(pattern)
        is_bad = False

        for f in filepaths:
            message = Text(f'Test: {f.name}')
            message.append(_get_size_text(f))
            code = 0

            with Log.status(message):
                code = Run.run([_zipper, 't', f])

            if code > 0:
                Log.fail(message)
                is_bad = True
            else:
                Log.ok(message)
        
        if is_bad:
            raise ArchiveMachineError()

    def delete_files(self, paths):
        cull = 'Cull: '
        ok = True

        for f in paths:
            size = _get_size_text(f)
            status = Text(cull).append(Text(f.name)).append(size)

            with Log.status(status):
                try:
                    f.unlink()
                except OSError as e:
                    status.append(' ').append(e.strerror)
                    Log.fail(status)
                    ok = False
                    continue
                except Exception as e:
                    Log.fail(status)
                    ok = False
                    continue
            
            size.stylize('strike')
            status = Text(cull).append(Text(f.name, style='strike gray58')).append(size)
            Log.ok(status)

        return ok

    def op_cull(self, step):
        keep = step.get('keep')
        retention = step.get('retention')

        if (keep is None) and (retention is None):
            raise ArchiveMachineError('Cull: Must specify either retention or keep')
       
        filepaths = self.get_siblings_glob(self.get_all_dates_pattern())
        filepaths = sorted(filepaths)
        deletions = None

        if keep is not None:
            if type(keep) is not int or keep < 1:
                raise ArchiveMachineError('Cull: keep must be greater than 0')
        
            cull_count = max(0, len(filepaths) - keep)
            deletions = filepaths[:cull_count]

        if retention is not None:
            duration = None

            if type(retention) is str:
                retention = 'P' + ''.join(retention.split())
                duration = _parse_iso_duration(retention)

            if not duration:
                raise ArchiveMachineError('Cull: Invalid retention format')
            
            if not _is_at_least_one_day(duration):
                raise ArchiveMachineError('Cull: retention must be at minimum one day')

            deletions = _get_files_older_than(filepaths, duration)

        if not self.delete_files(deletions):
            raise ArchiveMachineError()
