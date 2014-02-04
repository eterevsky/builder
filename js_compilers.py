from . import action, File


@action
def concatenate(js_files):
  concatenation = '\n'.join(js_file.read() for js_file in js_files)
  out = File.create_temp()
  out.write(concatenation)
  return out


class ConcatenateCompiler(object):
  def __init__(self):
    self.name = 'concatenate'

  def test(self):
    return True

  def compile(self, js_files):
    return concatenate(js_files)


class ClosureCompiler(object):
  def __init__(self):
    self.name = 'closure'

  def test(self):
    return False  # Not implemented


class UglifyJSCompiler(object):
  def __init__(self):
    self.name = 'uglifyjs'

  def test(self):
    return False  # Not implemented
