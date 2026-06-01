from src_build import common

DOIT_CONFIG = common.init(python_paths=['src_py', 'src_build'],
                          default_tasks=['wheel'])

from src_doit import *  # NOQA
