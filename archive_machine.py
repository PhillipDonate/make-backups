from isodate import Duration, isoerror
from statemachine import StateMachine, State
from pathlib import Path
from datetime import date, datetime, timedelta
from rich.text import Text
from itertools import chain
import sys
import subprocess
import isodate
import shutil
import paths
import log

class ArchiveMachineError(Exception):
    pass

_archive_extension_to_arguments = {
    'zip': ['--format=zip', '-cf'],
    'tar': '-cf',
    'tgz': '-czf',
    'tar.gz': '-czf',
    'tar.xz': '-cJf',
}

def _flatten(lst):
    return list(chain.from_iterable(
        _flatten(i) if isinstance(i, list) else [i] for i in lst
    ))

def _get_output_from_step(step):
    if step.get('show_output'):
        return None
    return subprocess.DEVNULL

def _run(args, input=None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
    return subprocess.run(args=_flatten(args), input=input, stdout=stdout, stderr=stderr)

def _parse_iso_duration(s: str) -> Duration:
    try:
        return isodate.parse_duration(s, as_timedelta_if_possible=False)
    except isoerror.ISO8601Error:
        return None

def _get_files_older_than(path_list: list[Path], duration: Duration):
    today = date.today()
    cutoff = today - duration
    deletions = []

    for p in path_list:
        try:
            _, datestr = p.stem.rsplit('_', 1)
            file_date = datetime.strptime(datestr, '%Y-%m-%d').date()
        except Exception:
            continue

        if file_date < cutoff:
            deletions.append(p)

    return deletions

def _get_size_text(path: Path) -> Text:
    size = path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            size = f'{size:.2f} {unit}'
            break
        size /= 1024
    style = 'dim italic grey50'
    text = Text('  ', style=style)
    return text.append(Text(size, style=style))

def _is_at_least_one_day(d: Duration) -> bool:
    today = date.today()
    future = today + d
    return (future - today) >= timedelta(days=1)

class ArchiveMachine(StateMachine):
    start = State(initial=True)
    packing = State()
    running = State()
    finish = State(final=True)

    # Transitions
    next = start.to(packing) | packing.to(running) | running.to(running)
    complete = running.to(finish) | packing.to(finish)

    def __init__(self, name, steps):
        super().__init__()
        self.name = name
        self.steps = steps
        self.index = 0
        self.failed = False
        self.encrypted = False
        self.filename = None
        self.filesuffix = None
        self.filepath = None

    @property
    def finished(self) -> bool:
        return self.finish.is_active

    def fail(self, e: Exception = None):
        if e:
            message = str(e)
            log.fail(Text(message))

        self.failed = True
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

        except Exception as e:
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
                case 'exec':
                    self.op_exec(step)
                case 'pack':
                    raise ArchiveMachineError(f'{self.name}: Cannot pack again')
                case _:
                    raise ArchiveMachineError(f'{self.name}: Unknown op: {op}')

        except Exception as e:
            self.fail(e)

    def op_pack(self, step):
        zip = step.get('zip') or ('zip' if sys.platform == 'win32' else 'tgz')
        src = step.get('in')
        out = step.get('out')

        if not (src and out):
            raise ArchiveMachineError(f'{self.name}: Pack must specify "in" and "out"')

        if not paths.tar.is_file():
            raise ArchiveMachineError(f'Not found: {paths.tar}')

        source = Path(src)
        target = Path(out)

        if not source.exists():
            raise ArchiveMachineError(f'Not found: {source}')

        if not target.exists():
            raise ArchiveMachineError(f'Not found: {target}')

        zip_args = _archive_extension_to_arguments.get(zip)

        if not zip_args:
            raise ArchiveMachineError(f'Unsupported archive format: {zip}')

        encryption_key = step.get('encryption_key')

        if encryption_key:
            encryption_key = Path(encryption_key)

            if not encryption_key.is_file():
                raise ArchiveMachineError(f'Not found: {encryption_key}')
            
            if not paths.age.is_file():
                raise ArchiveMachineError(f'Not found: {paths.age}')

            zip = f'{zip}.age'
            self.encrypted = True

        today = date.today().strftime('%Y-%m-%d')
        self.filesuffix = f'.{zip}'
        self.filename = self.name + f'_{today}{self.filesuffix}'
        self.filepath = target / self.filename

        if self.filepath.is_file():
            self.filepath.unlink()

        source_name = source.name
        source_parent = source.parent

        if not source_name:
            source_name = '.'
            source_parent = str(source)

        output = _get_output_from_step(step)
        lock = ' 🔒' if self.encrypted else ''
        message = Text(f'Pack: {self.filename}{lock}')

        with log.status(message):
            if self.encrypted:
                result = _run(
                    [ paths.tar, zip_args, '-', '-C', source_parent, source_name ],
                    stdout=subprocess.PIPE,
                    stderr=output
                )
                result = _run(
                    [ paths.age, '-e', '-R', encryption_key, '-o', self.filepath ],
                    input=result.stdout,
                    stdout=output,
                    stderr=output
                )
            else:
                result = _run(
                    [ paths.tar, zip_args, self.filepath, '-C', source_parent, source_name ],
                    stdout=output,
                    stderr=output
                )

        if result.returncode > 0:
            raise ArchiveMachineError(message)

        message.append(_get_size_text(self.filepath))
        log.ok(message)

    def op_move(self, step):
        to = step.get('to')

        if not to:
            raise ArchiveMachineError(f'{self.name}: Move must specify "to"')

        target = Path(to)

        if not target.exists():
            raise ArchiveMachineError(f'Not found: {target}')
        
        if not target.is_dir():
            raise ArchiveMachineError(f'Not a directory: {target}')
        
        message = Text(f'Move: {self.filename} -> {target}')
        message.append(_get_size_text(self.filepath))
        
        with log.status(message):
            try:
                self.filepath = Path(shutil.move(self.filepath, target / self.filename))

            except OSError as e:
                message.append(' ').append(e.strerror)
                raise ArchiveMachineError(message)

            except Exception:
                raise ArchiveMachineError(message)

        log.ok(message)

    def op_exec(self, step):
        tool_path = step.get('path')

        if not tool_path:
            raise ArchiveMachineError('Exec: path not specified')
        
        tool_path = Path(tool_path)

        if not tool_path.is_file():
            raise ArchiveMachineError(f'Not found: {tool_path}')
        
        output = _get_output_from_step(step)
        message = Text(f'Exec: {self.filename} -> {tool_path.name}')
    
        with log.status(message):
            result = _run(
                [ tool_path, self.filepath, self.filename, self.name ],
                stdout=output,
                stderr=output
            )

        if result.returncode > 0:
            raise ArchiveMachineError(message)

        log.ok(message)

    def get_all_dates_pattern(self):
        return f'{self.name}_????-??-??{self.filesuffix}'

    def get_siblings_glob(self, pattern):
        return self.filepath.parent.glob(pattern)

    def op_test(self, step):
        if self.encrypted:
            raise ArchiveMachineError(f'Cannot test encrypted archive: {self.filename}')

        if not paths.tar.is_file():
            raise ArchiveMachineError(f'Not found: {paths.tar}')
    
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

            with log.status(message):
                code = _run([paths.tar, '-tf', f]).returncode

            if code > 0:
                log.fail(message)
                is_bad = True
            else:
                log.ok(message)
        
        if is_bad:
            raise ArchiveMachineError()

    def delete_files(self, path_list):
        cull = 'Cull: '
        ok = True

        for f in path_list:
            size = _get_size_text(f)
            status = Text(cull).append(Text(f.name)).append(size)

            with log.status(status):
                try:
                    f.unlink()
                except OSError as e:
                    status.append(' ').append(e.strerror)
                    log.fail(status)
                    ok = False
                    continue
                except Exception as e:
                    log.fail(status)
                    ok = False
                    continue
            
            size.stylize('strike')
            status = Text(cull).append(Text(f.name, style='strike gray58')).append(size)
            log.ok(status)

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
