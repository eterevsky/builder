from . import action, File
from . import js_compilers


COMPILER_PREFERENCE = ['closure', 'uglifyjs', 'concatenate']

COMPILER_CLASS = {
  'closure': js_compilers.ClosureCompiler,
  'uglifyjs': js_compilers.UglifyJSCompiler,
  'concatenate': js_compilers.ConcatenateCompiler
}

# TODO: Make this generic for all compilers, not just JS.
def get_compiler(preference=None):
  if preference is None:
    preference = COMPILER_PREFERENCE

  for comp_name in preference:
    compiler = COMPILER_CLASS[comp_name]()
    if compiler.test():
      return compiler


@action
def concatenate(source_files):
  res = ''
  for f in source_file:
    res += f.read() + '\n'
  return res


@action
def compile(source_files, target_path, method='concatenate'):
  if method == 'concatenate':
    out = File(target_path)
    out.write(concatentae(source_files))
    return out
  raise Exception()
