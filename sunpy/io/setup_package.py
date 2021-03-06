import os
import platform
from glob import glob
from distutils.core import Extension

from astropy_helpers import setup_helpers


def get_extensions():

    if platform.system() == 'Windows':
        return list()
    else:
        # 'numpy' will be replaced with the proper path to the numpy includes
        cfg = setup_helpers.DistutilsExtensionArgs()
        cfg['include_dirs'].append('numpy')
        cfg['sources'].extend(sorted(glob(
            os.path.join(os.path.dirname(__file__), 'src', 'ana', '*.c'))))
        cfg['extra_compile_args'].extend(['-std=c99', '-O3'])
        # Squash some warnings
        cfg['extra_compile_args'].extend(['-Wno-unused-but-set-variable',
                                          '-Wno-unused-variable',
                                          '-Wno-unused-result',
                                          '-Wno-sign-compare'])

        e = Extension('sunpy.io._pyana', **cfg)
        return [e]
