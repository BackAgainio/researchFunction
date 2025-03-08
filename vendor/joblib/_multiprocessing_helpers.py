"""Helper module to factorize the conditional multiprocessing import logic
...
"""

import os
import warnings

# Explicitly disable multiprocessing if JOBLIB_MULTIPROCESSING is 0
if int(os.environ.get('JOBLIB_MULTIPROCESSING', 1)) == 0:
    mp = None
else:
    try:
        import multiprocessing as mp
        import _multiprocessing  # noqa
    except ImportError:
        mp = None

# 2nd stage: validate that locking is available on the system and
#            issue a warning if not
if mp is not None:
    try:
        import tempfile
        from _multiprocessing import SemLock

        _rand = tempfile._RandomNameSequence()
        for i in range(100):
            try:
                name = '/joblib-{}-{}'.format(os.getpid(), next(_rand))
                _sem = SemLock(0, 0, 1, name=name, unlink=True)
                del _sem  # cleanup
                break
            except FileExistsError as e:
                if i >= 99:
                    raise FileExistsError('cannot find name for semaphore') from e
    except (FileExistsError, AttributeError, ImportError, OSError) as e:
        mp = None
        warnings.warn('%s.  joblib will operate in serial mode' % (e,))

# 3rd stage: backward compat for the assert_spawning helper
if mp is not None:
    from multiprocessing.context import assert_spawning
else:
    assert_spawning = None

