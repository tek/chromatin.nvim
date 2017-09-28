from typing import Callable
import sys
import venv
from pathlib import Path
import subprocess

nvim_inst = None


def nvim(f: Callable) -> None:
    global nvim_inst
    if nvim_inst is None:
        try:
            import neovim
            nvim_inst = neovim.attach('stdio')
        except Exception as e:
            pass
    if nvim_inst is not None:
        f(nvim_inst)


def echo(msg: str) -> None:
    nvim(lambda a: a.command(f'echo "{msg}"'))


def amino_logger() -> None:
    from amino.logging import amino_root_logger, amino_file_logging
    amino_file_logging(amino_root_logger)
    return amino_root_logger


def check_result(result: subprocess.CompletedProcess) -> None:
    msg = str(result).replace('"', '')
    if result.returncode != 0:
        echo(f'subprocess failed: {msg}')
        sys.exit(1)


def install(venv_dir: str, builder: venv.EnvBuilder, bin_path: Path) -> None:
    echo('installing chromatin...')
    req = sys.argv[2]
    builder.create(venv_dir)
    pip = bin_path / 'pip'
    args = [str(pip), 'install', '-U', '--no-cache', req]
    result = subprocess.run(args, env=dict(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    check_result(result)


def start(run: Path, exe: str, bin: str, installed: int) -> None:
    result = subprocess.run([exe, str(run), exe, bin, str(installed)], env=dict())
    check_result(result)


def bootstrap() -> None:
    venv_dir = sys.argv[1]
    builder = venv.EnvBuilder(system_site_packages=False, with_pip=True)
    ns = builder.ensure_directories(venv_dir)
    bin = Path(ns.bin_path)
    run = bin / 'crm_run'
    installed = 0
    if not Path(run).exists():
        installed = 1
        install(venv_dir, builder, bin)
        echo('initializing chromatin...')
    start(run, ns.env_exe, ns.bin_path, installed)

try:
    bootstrap()
    sys.exit(0)
except Exception as e:
    try:
        echo(f'error while bootstrapping chromatin: {e}')
        amino_logger().caught_exception_error('bootstrapping chromatin', e)
    except Exception:
        pass
    sys.exit(1)
