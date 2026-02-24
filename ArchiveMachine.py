from statemachine import StateMachine, State
from pathlib import Path
from datetime import date
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

        message = f'Pack: {self.filename}'
        code = 0

        with Log.status(message):
            cmd = [ _zipper, "a", "-mx9", self.filepath, source ]
            code = Run.run(cmd)

        if code > 0:
            self.fail(message)
        else:
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
        
        message = f'Move: {self.filename} -> {target}'
        
        with Log.status(message):
            try:
                self.filepath = Path(shutil.move(self.filepath, target / self.filename))
            except Exception as e:
                self.fail(f'{message} {e}')
                return
        
        Log.ok(message)

    def op_test(self, step):
        if not _zipper.exists():
            self.fail(f"Not found: {_zipper}")
            return
    
        pattern = step.get('pattern') or self.filename
        filepaths = self.filepath.parent.glob(pattern)
        is_bad = False

        for f in filepaths:
            message = f'Test: {f.name}'
            code = 0

            with Log.status(message):
                code = Run.run([_zipper, "t", self.filepath])

            if code > 0:
                Log.fail(message)
                is_bad = True
            else:
                Log.ok(message)
        
        if is_bad:
            self.fail()
