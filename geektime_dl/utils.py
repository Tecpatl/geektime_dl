# coding=utf8
import contextlib
import threading
import pathlib
from functools import wraps
from typing import List

_working_folder = pathlib.Path.home() / '.geektime_dl'
_working_folder.mkdir(exist_ok=True)


def get_working_folder():
    return _working_folder


def synchronized(lock_attr='_lock'):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            lock = getattr(self, lock_attr)
            try:
                lock.acquire()
                return func(self, *args, **kwargs)
            finally:
                lock.release()
        return wrapper
    return decorator


class Singleton(type):
    _instances = {}
    _lock = threading.Lock()

    @synchronized()
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    @classmethod
    @synchronized()
    def clear_singletons(cls):
        return cls._instances.clear()


def read_cookies_from_file(file_path: pathlib.Path) -> dict:
    cookies = {}
    with open(file_path, 'r') as f:
        for line in f.read().split(';'):
            n, v = line.split('=', 1)
            with contextlib.suppress(Exception):
                _ = v.strip().encode('latin-1')
                cookies[n.strip()] = v.strip()
    return cookies


def read_local_cookies() -> dict:
    fn = get_working_folder() / 'cookies'
    if not fn.exists():
        return {}
    return read_cookies_from_file(fn)


def parse_column_ids(ids_str: str) -> List[int]:
    def _int(num):
        try:
            return int(num)
        except Exception:
            raise ValueError('illegal column ids: {}'.format(ids_str))
    res = list()
    segments = ids_str.split(',')
    for seg in segments:
        if '-' in seg:
            s, e = seg.split('-', 1)
            res.extend(range(_int(s), _int(e) + 1))
        else:
            res.append(_int(seg))
    res = list(set(res))
    res.sort()
    return res
