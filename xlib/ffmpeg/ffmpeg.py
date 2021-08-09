import json
import subprocess
from typing import Union

def run(args, pipe_stdin=False, pipe_stdout=False, pipe_stderr=False, quiet_stderr=False) -> Union[subprocess.Popen,None]:
    """
    run ffmpeg process

    returns Popen class if success
    otherwise None
    """
    args = ['ffmpeg'] + args

    stdin_stream = subprocess.PIPE if pipe_stdin else None
    stdout_stream = subprocess.PIPE if pipe_stdout else None
    stderr_stream = subprocess.PIPE if pipe_stderr else None

    if quiet_stderr and not pipe_stderr:
        stderr_stream = subprocess.DEVNULL

    try:
        return subprocess.Popen(args, stdin=stdin_stream, stdout=stdout_stream, stderr=stderr_stream)
    except Exception as e:
        print('ffmpeg exception: ', e)
    return None


def probe(filename):
    """Run ffprobe on the specified file and return a JSON representation of the output.

    Raises:
        Exception if ffprobe returns a non-zero exit code,
    """
    args = ['ffprobe', '-show_format', '-show_streams', '-of', 'json', filename]

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise Exception('ffprobe', out, err)
    return json.loads(out.decode('utf-8'))

def probe(filename):
    """Run ffprobe on the specified file and return a JSON representation of the output.

    Raises:
        Exception if ffprobe returns a non-zero exit code,
    """
    args = ['ffprobe', '-show_format', '-show_streams', '-of', 'json', filename]
    #'-count_frames',

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise Exception('ffprobe', out, err)
    return json.loads(out.decode('utf-8'))

