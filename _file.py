import os

# TODO: make File a file-like object, opening the underling file descriptor
# on demand. Think about the
class File(object):
  @staticmethod
  def create_temp():
    return InMemoryFile()

  def __init__(self, path):
    self.path = path

  def __truediv__(self, subpath):
    return File(os.path.join(self.path, subpath))

  def __repr__(self):
    return 'File(\'' + self.path + '\')'

  def __str__(self):
    if self.path.startswith('./'):
      return self.path[2:]
    return self.path

  def isdir(self):
    return os.path.isdir(self.path)

  def read(self, mode=''):
    with open(self.path, 'r' + mode) as f:
      return f.read()

  def write(self, data, mode=''):
    os.makedirs(os.path.dirname(self.path), exist_ok=True)
    with open(self.path, 'w' + mode) as f:
      return f.write(data)

  def append(self, data):
    os.makedirs(os.path.dirname(self.path), exist_ok=True)
    with open(self.path, 'a') as f:
      return f.write(data)


class InMemoryFile(object):
  def __init__(self):
    self._buffer = ''

  def __repr__(self):
    return 'InMemoryFile()'

  def __str__(self):
    return '<TEMP>'

  def isdir(self):
    return False

  @property
  def path(self):
    # TODO: Create a real temporary file and return its path.
    raise Exception('Not implemented')

  def write(self, data):
    self._buffer = data

  def read(self, mode=''):
    if mode == 'b':
      return bytes(self._buffer, 'utf-8')
    return self._buffer

  def append(self, data):
    self._buffer += data
