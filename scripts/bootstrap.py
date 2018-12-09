import os
import sys
import venv
import shutil
import logging
from pathlib import Path
import subprocess
from subprocess import PIPE

nvim_inst = None
amino_log_inst = None
development = 'AMINO_DEVELOPMENT' in os.environ
debug_env_var = 'CHROMATIN_DEBUG'
debug_log_file = '/tmp/chromatin_debug'


def echo(msg: str) -> None:
    truncated = msg[:511]
    padding = 511 - len(truncated)
    padded = truncated + '\x00' * padding
    data = b'\x93\x02\xaenvim_out_write\x91\xda\x02\x00' + padded.encode() + b'\n'
    sys.stdout.buffer.write(data)
    sys.stdout.flush()
    logging.debug(msg)


def check_result(result: subprocess.CompletedProcess) -> None:
    msg = str(result).replace('"', '')
    logging.debug(f'bootstrap subproc result: {result}')
    if result.returncode != 0:
        raise Exception(f'subprocess failed: {msg}')


def subproc(*args: str, pipe: bool=True) -> None:
    isolate = sys.argv[4] == '1'
    env = (dict(AMINO_DEVELOPMENT='1') if development else dict()) if isolate else None
    kw = dict(stdout=PIPE) if pipe else dict()
    logging.debug(f'bootstrap subproc: {args}')
    result = subprocess.run(args, env=env, stderr=PIPE, **kw)
    check_result(result)


def virtualenv_interpreter(venv: str, executable: str) -> str:
    path = os.getenv('PATH', '').split(':')
    clean_path = [a for a in path if not a.startswith(venv)]
    candidate = shutil.which(executable, path=':'.join(clean_path))
    if candidate is None:
        raise Exception(f'no non-virtualenv python interpreter for `{executable}` found in $PATH')
    return candidate


def python_interpreter() -> str:
    spec = sys.argv[3]
    venv = os.getenv('VIRTUAL_ENV', '[no venv]')
    return (
        spec
        if Path(spec).exists() else
        virtualenv_interpreter(venv, spec)
    )


def create_venv(dir: str) -> None:
    subproc(python_interpreter(), '-m', 'venv', str(dir), '--upgrade')


def install(venv_dir: str, bin_path: Path) -> None:
    echo('installing chromatin...')
    req = sys.argv[2]
    pip = bin_path / 'pip'
    subproc(str(pip), 'install', '-U', '--no-cache', 'pip')
    subproc(str(pip), 'install', '-U', '--no-cache', req)


def start(run: Path, exe: str, bin: str, installed: int) -> None:
    subproc(exe, str(run), exe, bin, str(installed), pipe=False)


def setup_debug_log() -> None:
    if development or debug_env_var in os.environ:
        logging.basicConfig(filename=debug_log_file, level=logging.DEBUG)
    logging.debug('starting chromatin bootstrap')


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
    setup_debug_log()
    bootstrap()
    sys.exit(0)
except Exception as e:
    msg = f'error while bootstrapping chromatin: {e}'
    try:
        logging.debug(msg)
        echo(f'fatal error while initializing chromatin. set ${debug_env_var} and inspect {debug_log_file}')
    except Exception:
        pass
    sys.exit(1)
