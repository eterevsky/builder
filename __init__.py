import argparse
import inspect
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


def unwrap_function(func):
  try:
    return func.__func
  except AttributeError:
    return func


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

  @action
  def copy(self, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy(self.path, dest_path)
    return File(dest_path)


def add_builder_arguments(arg_parser):
  arg_parser.add_argument('-v', '--verbose', help='make output more verbose',
                          action='count')

def add_command_arguments(command, parser, defaults):
  args = inspect.getfullargspec(command)
  if args.defaults is not None:
    no_defaults = len(args.args) - len(args.defaults)
    args_defaults = [None] * no_defaults + list(args.defaults)
  else:
    args_defaults = [None] * len(args.args)

  for i in range(len(args.args)):
    name = args.args[i]
    default = args_defaults[i]

    if default is None and name in defaults:
      default = defaults[name]

    if name in args.annotations:
      argtype = args.annotations[name]
    else:
      argtype = None

    if argtype is File:
      argtype = str

    if default is False and (not argtype or argtype is bool):
      parser.add_argument('--' + name, action='store_true')
    else:
      if default is not None:
        arghelp = '[default=' + str(default) + ']'
      else:
        arghelp = None
      # TODO: Generate arguments help from the docstring
      parser.add_argument('--' + name, type=argtype, default=default,
                          help=arghelp)

def run_build(func, arguments):
  kwargs = {}
  fargs = inspect.getfullargspec(func)

  for name in fargs.args:
    if name in fargs.annotations and fargs.annotations[name] is File:
      kwargs[name] = File(arguments[name])
    else:
      kwargs[name] = arguments[name]

  func(**kwargs)


def run(*cmds):
  parser = argparse.ArgumentParser()
  add_builder_arguments(parser)

  defaults = {}
  build_script = unwrap_function(cmds[0]).__globals__['__file__']
  defaults['source_dir'] = os.path.dirname(build_script) or '.'
  defaults['base_build_path'] = os.path.join(defaults['source_dir'], 'build')

  if len(cmds) == 1:
    func = unwrap_function(cmds[0])
    parser.set_defaults(func=func)
    add_command_arguments(func, parser, defaults)
  else:
    subparsers = parser.add_subparsers()
    for func in cmds:
      func = unwrap_function(func)
      subparser = subparsers.add_parser(func.__name__, help=func.__doc__)
      subparser.set_defaults(func=func)
      add_command_arguments(func, subparser, defaults)

  args = parser.parse_args()

  run_build(args.func, vars(args))

