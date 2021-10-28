"""
Job lib using subprocesses
"""

import multiprocessing
if multiprocessing.get_start_method() != 'spawn':
    multiprocessing.set_start_method("spawn", force=True)

from .run_sequence import run_sequence