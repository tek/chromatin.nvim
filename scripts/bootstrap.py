import os
import sys
import venv
import logging
from pathlib import Path
import subprocess
from subprocess import PIPE

nvim_inst = None
amino_log_inst = None
development = 'AMINO_DEVELOPMENT' in os.environ


def amino_logger() -> None:
    global amino_log_inst
    if amino_log_inst is None:
        from amino.logging import amino_root_logger, amino_root_file_logging
        amino_root_file_logging()
        amino_log_inst = amino_root_logger
    return amino_log_inst


def amino_log(msg: str) -> None:
    try:
        amino_logger().debug(msg)
    except Exception as e:
        pass


def echo(msg: str) -> None:
    amino_log(msg)


def tmpfile_error(msg: str) -> None:
    try:
        import tempfile
        (fh, file) = tempfile.mkstemp(prefix='chromatin-bootstrap')
        Path(file).write_text(msg)
    except Exception as e:
        pass


def check_result(result: subprocess.CompletedProcess) -> None:
    msg = str(result).replace('"', '')
    logging.debug(f'bootstrap subproc result: {result}')
    if result.returncode != 0:
        echo(f'subprocess failed: {msg}')
        sys.exit(1)


def subproc(*args: str, pipe: bool=True) -> None:
    isolate = sys.argv[4] == '1'
    env = (dict(AMINO_DEVELOPMENT='1') if development else dict()) if isolate else None
    kw = dict(stdout=PIPE) if pipe else dict()
    logging.debug(f'bootstrap subproc: {args}')
    result = subprocess.run(args, env=env, stderr=PIPE, **kw)
    check_result(result)


def create_venv(dir: str) -> None:
    interpreter = sys.argv[3]
    subproc(interpreter, '-m', 'venv', str(dir), '--upgrade')


def install(venv_dir: str, bin_path: Path) -> None:
    echo('installing chromatin...')
    req = sys.argv[2]
    pip = bin_path / 'pip'
    subproc(str(pip), 'install', '-U', '--no-cache', 'pip')
    subproc(str(pip), 'install', '-U', '--no-cache', req)


def start(run: Path, exe: str, bin: str, installed: int) -> None:
    subproc(exe, str(run), exe, bin, str(installed), sys.argv[5], pipe=False)


def bootstrap() -> None:
    venv_dir = sys.argv[1]
    create_venv(venv_dir)
    builder = venv.EnvBuilder(system_site_packages=False, with_pip=True)
    ns = builder.ensure_directories(venv_dir)
    bin = Path(ns.bin_path)
    run = bin / 'crm_run'
    installed = 0
    if not Path(run).exists():
        installed = 1
        install(venv_dir, bin)
        echo('initializing chromatin...')
    start(run, ns.env_exe, ns.bin_path, installed)

try:
    debug_log = sys.argv[5]
    if debug_log:
        logging.basicConfig(filename=debug_log, level=logging.DEBUG)
    logging.debug('starting chromatin bootstrap')
    bootstrap()
    sys.exit(0)
except Exception as e:
    msg = f'error while bootstrapping chromatin: {e}'
    try:
        tmpfile_error(msg)
        echo(msg)
        amino_logger().caught_exception_error('bootstrapping chromatin', e)
    except Exception:
        print(msg, file=sys.stderr)
    sys.exit(1)
