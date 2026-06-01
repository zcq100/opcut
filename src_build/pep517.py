"""Minimal PEP 517 build backend (replaces hat.doit.pep517)."""

from pathlib import Path
import subprocess
import sys

from . import common


class UnsupportedOperation(Exception):
    pass


def build_wheel(wheel_directory,
                config_settings=None,
                metadata_directory=None):
    """Build a wheel by calling the doit wheel task."""
    return _build_wheel(Path(wheel_directory), False)


def build_editable(wheel_directory,
                   config_settings=None,
                   metadata_directory=None):
    """Build an editable wheel by calling the doit wheel task."""
    return _build_wheel(Path(wheel_directory), True)


def build_sdist(sdist_directory, config_settings=None):
    """Source distribution is not supported."""
    raise UnsupportedOperation()


def get_requires_for_build_wheel(config_settings=None):
    """Return the build requirements for building a wheel."""
    return list(_get_requires())


def get_requires_for_build_editable(config_settings=None):
    """Return the build requirements for building an editable wheel."""
    return list(_get_requires())


def _build_wheel(whl_dir, editable):
    """Internal: build a wheel by invoking doit."""
    conf = common.get_conf()
    tool_conf = conf.get('tool', {}).get('hat-doit', {})

    task = tool_conf.get('build_wheel_task', 'wheel')

    whl_name_path = whl_dir / 'wheel_name'
    subprocess.run([sys.executable, '-m', 'doit', task,
                    '--whl-dir', str(whl_dir),
                    '--whl-name-path', str(whl_name_path),
                    *(['--editable'] if editable else [])],
                   check=True)
    return whl_name_path.read_text()


def _get_requires():
    """Get the build requirements."""
    yield 'doit'
    yield 'mkwhl'
    yield 'packaging'
    yield 'watchdog'
