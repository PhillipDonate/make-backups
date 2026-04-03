from statemachine import StateMachine, State
from archive_machine import ArchiveMachine
from rich.text import Text
from pathlib import Path
import shutil
import log
import os

class MainMachineError(Exception):
    pass

class MainMachine(StateMachine):
    start = State(initial=True)
    prepping = State()
    archiving = State()
    finishing = State()
    completed = State(final=True)

    go = start.to(prepping)
    next = prepping.to(archiving) | archiving.to(finishing) | finishing.to(completed)
    fault = prepping.to(completed) | archiving.to(finishing) | finishing.to(completed)

    def __init__(self, prep_steps, finish_steps, workers: list[ArchiveMachine]):
        super().__init__()
        self.prep_steps = prep_steps
        self.finish_steps = finish_steps
        self.workers = workers
        self.failed = False

    def fail(self, e: Exception = None):
        if e:
            message = str(e)
            log.fail(Text(message))

        self.failed = True
        self.fault()

    def do_ops(self, steps):
        try:
            for step in steps:
                op = step.get('op')

                match(op):
                    case 'rmdir':
                        self.op_rmdir(step)
                    case 'mkdir':
                        self.op_mkdir(step)
                    case _:
                        raise MainMachineError(f'Unknown op: {op}')                   
            self.next()

        except Exception as e:
            self.fail(e)

    def on_enter_prepping(self):
        self.do_ops(self.prep_steps)

    def on_enter_finishing(self):
        self.do_ops(self.finish_steps)

    def on_enter_archiving(self):
        while True:
            active_workers = [m for m in self.workers if not m.finished]

            if not active_workers:
                break

            for m in active_workers:
                m.next()

        failed_workers = [m for m in self.workers if m.failed]

        if failed_workers:
            self.fail()
        else:
            self.next()

    def on_enter_completed(self):
        pass

    def op_rmdir(self, step):
        path = step.get('path')

        if not path:
            raise MainMachineError('rmdir: must specifiy "path"')

        path = Path(path)

        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=step.get('ignore_errors'))

    def op_mkdir(self, step):
        path = step.get('path')

        if not path:
            raise MainMachineError('mkdir: must specifiy "path"')

        os.mkdir(Path(path))
