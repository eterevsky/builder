import os
import shutil

def action(func):
  """Decorator for buider actions.

  Currently does nothing.
  TODO: Add auto-logging.
  TODO: Cache results.
  TODO: Run actions concurrently.
  TODO: Apply to classes to make class- and function-based actions
  interchangeable.
  """
  def wrapped_func(*args, **kargs):
    print(func.__name__, str(args), kargs if len(kargs) else '')
    return func(*args, **kargs)
  wrapped_func.__func = func
  return wrapped_func

@action
def copy(src_file, dest_path):
  os.makedirs(os.path.dirname(dest_path), exist_ok=True)
  shutil.copy(src_file.path, dest_path)
  return File(dest_path)

  
class File(object):
  def __init__(self, path):
    self.path = path

  def __truediv__(self, subpath):
    return File(os.path.join(self.path, subpath))

  def __repr__(self):
    return 'File(\'' + self.path + '\')'

  def isdir(self):
    return os.path.isdir(self.path)

  def read(self):
    with open(self.path) as f:
      return f.read()

  def write(self, data):
    with open(self.path, 'w') as f:
      return f.write(data)

  def copy(self, dest_path):
    return copy(self, dest_path)


def run(main_build, source_path=None):
  if source_path is None:
    try:
      func = main_build.__func
    except AttributError:
      func = main_build
    source_path = os.path.dirname(func.__globals__['__file__']) or '.'
  source_dir = File(source_path)
  build_path = os.path.join(source_path, 'build')
  main_build(source_dir, build_path)