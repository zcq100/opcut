"""JavaScript/TypeScript build support (replaces hat.doit.js)."""

from pathlib import Path
import enum
import importlib.resources
import subprocess

from . import eslint as build_eslint


class ESLintConf(enum.Enum):
    JS = 'js'
    TS = 'ts'


def run_eslint(path: Path,
               conf: ESLintConf = ESLintConf.JS):
    """Run eslint on a path with the given configuration."""
    if conf == ESLintConf.JS:
        parser = 'espree'

    elif conf == ESLintConf.TS:
        parser = '@typescript-eslint/parser'

    else:
        raise ValueError('unsupported conf')

    package = importlib.resources.files(build_eslint)
    with importlib.resources.as_file(package /
                                     f'{conf.value}.yaml') as conf_path:
        subprocess.run(['npx', 'eslint',
                        '--parser', parser,
                        '--resolve-plugins-relative-to', '.',
                        '-c', str(conf_path),
                        str(path)],
                       check=True)
