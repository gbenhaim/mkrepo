"""Utils"""

import subprocess
import os
import errno
import logging
import uuid
from collections import namedtuple
import fcntl
import time

LOGGER = logging.getLogger(__name__)


_CommandStatus = namedtuple(
    'CommandStatus', ('code', 'out', 'err')
)


class CommandStatus(_CommandStatus):
    def __nonzero__(self):
        return self.code


def run_command(
    command,
    input_data=None,
    stdin=None,
    out_pipe=subprocess.PIPE,
    err_pipe=subprocess.PIPE,
    env=None,
    _uuid=None,
    **kwargs
):
    """
    Runs a command

    Args:
        command(list of str): args of the command to execute, including the
            command itself as command[0] as `['ls', '-l']`
        input_data(str): If passed, will feed that data to the subprocess
            through stdin
        out_pipe(int or file): File descriptor as passed to
            :ref:subprocess.Popen to use as stdout
        stdin(int or file): File descriptor as passed to
            :ref:subprocess.Popen to use as stdin
        err_pipe(int or file): File descriptor as passed to
            :ref:subprocess.Popen to use as stderr
        env(dict of str:str): If set, will use the given dict as env for the
            subprocess
        uuid(uuid): If set the command will be logged with the given uuid
            converted to string, otherwise, a uuid v4 will be generated.
        **kwargs: Any other keyword args passed will be passed to the
            :ref:subprocess.Popen call

    Returns:
        lago.utils.CommandStatus: result of the interactive execution
    """
    if env is None:
        env = os.environ.copy()

    if _uuid is None:
        _uuid = uuid.uuid4()

    if input_data and not stdin:
        kwargs['stdin'] = subprocess.PIPE
    elif stdin:
        kwargs['stdin'] = stdin

    if env is None:
        env = os.environ.copy()
    else:
        env['PATH'] = ':'.join(
            list(
                set(
                    env.get('PATH', '').split(':') + os.environ['PATH']
                    .split(':')
                ),
            ),
        )

    LOGGER.debug('Run command: {}'.format(' '.join(command)))

    popen = subprocess.Popen(
        ' '.join('"%s"' % arg for arg in command),
        stdout=out_pipe,
        stderr=err_pipe,
        shell=True,
        env=env,
        **kwargs
    )
    out, err = popen.communicate(input_data)
    LOGGER.debug(
        '%s: command exit with return code: %d', str(_uuid), popen.returncode
    )
    if out:
        LOGGER.debug('%s: command stdout: %s', str(_uuid), out)
    if err:
        LOGGER.debug('%s: command stderr: %s', str(_uuid), err)

    return CommandStatus(popen.returncode, out, err)


class Flock(object):
    """A wrapper class around flock

    Attributes:
        path(str): Path to the lock file
        readonly(bool): If true create a shared lock, otherwise
            create an exclusive lock.
        blocking(bool) If true block the calling process if the
            lock is already acquired.
    """

    def __init__(self, path, readonly=False, blocking=True):
        self._path = path
        self._fd = None
        if readonly:
            self._op = fcntl.LOCK_SH
        else:
            self._op = fcntl.LOCK_EX

        if not blocking:
            self._op |= fcntl.LOCK_NB

    @property
    def path(self):
        return self._path

    def acquire(self):
        """Acquire the lock

        Raises:
            IOError: if the call to flock fails
        """
        self._fd = open(self._path, mode='w+')
        fcntl.flock(self._fd, self._op)

    def release(self):
        if self._fd is not None:
            self._fd.close()


class TimerException(Exception):
    """
    Exception to throw when a timeout is reached
    """
    pass


class LockFiles(object):
    def __init__(self, paths, timeout=180, lock_name='lock.lock'):
        self._timeout = timeout
        self._lock_name = lock_name
        self._paths = sorted(paths)
        self._locks = []
        self._start_time = None
        self._sleep_duration = timeout / 10 or 1

    def _get_path_to_lock(self, path):
        return os.path.join(path, self._lock_name)

    def _time_left(self):
        return time.time() - self._start_time < self._timeout

    def __enter__(self):
        self._start_time = time.time()
        try:
            self._lock_all()
        except Exception as e:
            LOGGER.debug(str(e), exc_info=True)
            self._release_all()
            raise

    def _lock_all(self):
        for p in self._paths:
            self._locks.append(self._lock(p))
            LOGGER.info('Successfully locked {}'.format(p))

    def _lock(self, path):
        lock = Flock(
            path=self._get_path_to_lock(path),
            blocking=False
        )
        self._wait_for_lock(lock)

        return lock

    def _wait_for_lock(self, lock):
        while self._time_left():
            try:
                lock.acquire()
                break
            except IOError:
                time.sleep(self._sleep_duration)
        else:
            LOGGER.debug(
                'Got timeout while trying to lock {}'.format(lock.path)
            )
            err_msg = 'Failed to lock {} after {} seconds'.format(
                ','.join(self._paths),
                self._timeout
            )

            raise TimerException(err_msg)

    def _release_all(self):
        for lock in self._locks:
            lock.release()
            LOGGER.debug('Successfully released lock {}'.format(lock.path))

    def __exit__(self, *args):
        self._release_all()


def safe_mkdir(*path):
    for p in path:
        try:
            os.makedirs(p)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
