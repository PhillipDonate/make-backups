from statemachine import StateMachine, State
from pathlib import Path
from datetime import date
from rich.text import Text
import shutil
import Log
import Run

_zipper = Run.get_exe_dir() / '7za.exe'

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

    def fail(self, message=None):
        self.failed = True
        message and Log.fail(message)
        self.complete()

    def on_enter_packing(self):
        step = self.steps[self.index]
        op = step.get('op')

        match op:
            case 'pass':
                self.complete()
            case 'pack':
                self.op_pack(step)
            case _:
                self.fail(f'{self.name}: First step must be pack')
       
        self.index += 1

    def on_enter_running(self):
        if self.index >= len(self.steps):
            self.complete()
            return

        step = self.steps[self.index]
        op = step.get('op')

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
                self.fail(f'{self.name}: Cannot pack again')
            case _:
                self.fail(f'{self.name}: Unknown op: {op}')

        self.index += 1

    def op_pack(self, step):
        zip = step.get('zip') or 'zip'
        src = step['in']
        out = step['out']
    
        if not _zipper.exists():
            self.fail(f"Not found: {_zipper}")
            return

        source = Path(src)
        target = Path(out)

        if not source.exists():
            self.fail(f"Not found: {source}")
            return

        if not target.exists():
            self.fail(f"Not found: {target}")
            return

        today = date.today().strftime('%Y-%m-%d')
        self.filename = source.name + f'_{today}.{zip}'
        self.filepath = target / self.filename

        if self.filepath.is_file():
            self.filepath.unlink()

        message = Text(f'Pack: {self.filename}')
        code = 0

        with Log.status(message):
            cmd = [ _zipper, "a", "-mx9", self.filepath, source ]
            code = Run.run(cmd)

        if code > 0:
            self.fail(message)
        else:
            message.append(Log.get_size_text(self.filepath))
            Log.ok(message)

    def op_move(self, step):
        to = step['to']
        target = Path(to)

        if not target.exists():
            self.fail(f'Not found: {target}')
            return
        
        if not target.is_dir():
            self.fail(f'Not a directory: {target}')
            return
        
        message = Text(f'Move: {self.filename} -> {target}')
        message.append(Log.get_size_text(self.filepath))
        
        with Log.status(message):
            try:
                self.filepath = Path(shutil.move(self.filepath, target / self.filename))
            except OSError as e:
                message.append(' ').append(e.strerror)
                self.fail(message)
                return
            except Exception as e:
                self.fail(message)
                return
        
        Log.ok(message)

    def get_all_dates_pattern(self):
        return f'{self.name}_????-??-??{self.filepath.suffix}'
    
    def get_siblings_glob(self, pattern):
        return self.filepath.parent.glob(pattern)

    def op_test(self, step):
        if not _zipper.exists():
            self.fail(f"Not found: {_zipper}")
            return
    
        pattern = None

        if step.get('all_dates'):
            pattern = self.get_all_dates_pattern()
        else:
            pattern = step.get('pattern') or self.filename

        filepaths = self.get_siblings_glob(pattern)
        is_bad = False

        for f in filepaths:
            message = Text(f'Test: {f.name}')
            message.append(Log.get_size_text(f))
            code = 0

            with Log.status(message):
                code = Run.run([_zipper, "t", f])

            if code > 0:
                Log.fail(message)
                is_bad = True
            else:
                Log.ok(message)
        
        if is_bad:
            self.fail()

    def delete_files(self, paths):
        cull = 'Cull: '
        ok = True

        for f in paths:
            size = Log.get_size_text(f)
            status = Text(cull).append(Text(f.name))

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

        if (keep is None) == (retention is None):
            self.fail('Cull: Must specify either retention or keep')
            return
       
        filepaths = self.get_siblings_glob(self.get_all_dates_pattern())
        filepaths = sorted(filepaths)
        to_cull = None

        if keep is not None:
            if type(keep) is not int or keep < 1:
                self.fail('Cull: keep must be greater than 0')
                return
        
            cull_count = max(0, len(filepaths) - keep)
            to_cull = filepaths[:cull_count]
        else:
            to_cull = []

        if not self.delete_files(to_cull):
            self.fail()
