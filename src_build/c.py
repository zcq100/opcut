"""C build support (replaces hat.doit.c)."""

from pathlib import Path
from typing import Iterable
import functools
import os
import shlex
import shutil
import subprocess
import sysconfig

from . import common


def get_lib_suffix(platform: common.Platform = common.target_platform
                   ) -> str:
    """Get platform-specific shared library suffix."""
    if platform == common.Platform.WINDOWS_AMD64:
        return '.dll'

    if platform == common.Platform.DARWIN_X86_64:
        return '.dylib'

    if platform in (common.Platform.LINUX_GNU_X86_64,
                    common.Platform.LINUX_GNU_AARCH64,
                    common.Platform.LINUX_GNU_ARMV7L,
                    common.Platform.LINUX_MUSL_X86_64,
                    common.Platform.LINUX_MUSL_AARCH64,
                    common.Platform.LINUX_MUSL_ARMV7L):
        return '.so'

    raise ValueError('unsupported platform')


@functools.lru_cache
def get_cc(platform: common.Platform = common.target_platform
           ) -> str:
    """Get the C compiler path for the target platform."""
    candidates = []

    if platform == common.local_platform:
        if 'CC' in os.environ:
            candidates.append(os.environ['CC'])
        candidates.append('cc')
        candidates.append('gcc')

    if platform == common.Platform.WINDOWS_AMD64:
        candidates.append('x86_64-w64-mingw32-gcc')

    elif platform == common.Platform.LINUX_GNU_AARCH64:
        candidates.append('aarch64-linux-gnu-gcc')

    elif platform == common.Platform.LINUX_GNU_ARMV7L:
        candidates.append('arm-linux-gnueabihf-gcc')

    elif platform == common.Platform.LINUX_MUSL_X86_64:
        candidates.append('musl-gcc')

    for candidate in candidates:
        cmd = shutil.which(candidate)
        if cmd:
            return cmd

    raise ValueError('unsupported platform')


def get_c_flags(platform: common.Platform = common.target_platform
                ) -> Iterable[str]:
    """Get C compiler flags for the target platform."""
    yield from shlex.split(os.environ.get('CFLAGS', ''))

    if platform != common.local_platform:
        if platform == common.Platform.LINUX_GNU_ARMV7L:
            yield '-march=armv7'


def get_ld_flags(platform: common.Platform = common.target_platform,
                 shared: bool = False
                 ) -> Iterable[str]:
    """Get linker flags for the target platform."""
    if shared:
        if platform == common.Platform.WINDOWS_AMD64:
            yield '-mdll'
            yield '-Wl,--export-all'

        else:
            yield '-shared'

    yield from shlex.split(os.environ.get('LDFLAGS', ''))


def get_task_clang_format(src_paths: Iterable[Path]
                          ) -> Iterable[dict]:
    """Create tasks for formatting C source files with clang-format."""

    def clang_format(src_path):
        subprocess.run(['clang-format', '-i',
                        ('-style="{'
                         'BasedOnStyle: llvm, '
                         'IndentWidth: 4, '
                         'MaxEmptyLinesToKeep: 2, '
                         'TabWidth: 4'
                         '}"'),
                        str(src_path)],
                       check=True)

    for src_path in src_paths:
        yield {'name': str(src_path),
               'actions': [(clang_format, [src_path])],
               'file_dep': [src_path]}


class CBuild:
    """Helper for building C source files."""

    def __init__(self,
                 src_paths: list[Path],
                 build_dir: Path, *,
                 src_dir: Path = Path('.'),
                 platform: common.Platform = common.target_platform,
                 c_flags: list[str] = [],
                 ld_flags: list[str] = [],
                 ld_libs: list[str] = [],
                 task_dep: list[str] = []):
        self._src_paths = src_paths
        self._build_dir = build_dir
        self._src_dir = src_dir
        self._platform = platform
        self._c_flags = c_flags
        self._ld_flags = ld_flags
        self._ld_libs = ld_libs
        self._task_dep = task_dep

    def get_task_lib(self, lib_path: Path) -> dict:
        """Create a task that links a shared library."""
        obj_paths = [self._get_obj_path(src_path)
                     for src_path in self._src_paths]
        return {'name': str(lib_path),
                'actions': [(common.mkdir_p, [lib_path.parent]),
                            [get_cc(self._platform),
                             *get_ld_flags(self._platform, True),
                             *self._ld_flags,
                             '-o', str(lib_path),
                             *(str(obj_path) for obj_path in obj_paths),
                             *self._ld_libs]],
                'file_dep': obj_paths,
                'task_dep': self._task_dep,
                'targets': [lib_path]}

    def get_task_objs(self) -> dict:
        """Create tasks that compile .c files to .o files."""
        for src_path in self._src_paths:
            dep_path = self._get_dep_path(src_path)
            obj_path = self._get_obj_path(src_path)
            header_paths = _parse_dep(dep_path)
            yield {'name': str(obj_path),
                   'actions': [(common.mkdir_p, [obj_path.parent]),
                               [get_cc(self._platform),
                                '-c',
                                *get_c_flags(self._platform),
                                *self._c_flags,
                                '-o', str(obj_path),
                                str(src_path)]],
                   'file_dep': [src_path, dep_path, *header_paths],
                   'task_dep': self._task_dep,
                   'targets': [obj_path]}

    def get_task_deps(self) -> dict:
        """Create tasks that generate .d dependency files."""
        for src_path in self._src_paths:
            dep_path = self._get_dep_path(src_path)
            yield {'name': str(dep_path),
                   'actions': [(common.mkdir_p, [dep_path.parent]),
                               [get_cc(self._platform),
                                '-MM',
                                *get_c_flags(self._platform),
                                *self._c_flags,
                                '-o', str(dep_path),
                                str(src_path)]],
                   'file_dep': [src_path],
                   'task_dep': self._task_dep,
                   'targets': [dep_path]}

    def _get_dep_path(self, src_path):
        return (self._build_dir /
                src_path.relative_to(self._src_dir)).with_suffix('.d')

    def _get_obj_path(self, src_path):
        return (self._build_dir /
                src_path.relative_to(self._src_dir)).with_suffix('.o')


def _parse_dep(path):
    """Parse a .d dependency file to extract header paths."""
    if not path.exists():
        return

    content = path.read_text()
    if content:
        return

    content = content.split('\n')
    content[0] = content[0][content[0].find(':') + 1:]
    for i in content:
        for path_str in i.replace(' \\\n', '').strip().split(' '):
            yield Path(path_str)
