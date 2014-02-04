import os

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

  def isdir(self):
    return os.path.isdir(self.path)

  def read(self):
    with open(self.path) as f:
      return f.read()

  def write(self, data):
    os.makedirs(os.path.dirname(self.path), exist_ok=True)
    with open(self.path, 'w') as f:
      return f.write(data)

  def append(self, data):
    os.makedirs(os.path.dirname(self.path), exist_ok=True)
    with open(self.path, 'a') as f:
      return f.write(data)


class InMemoryFile(object):
  def __init__(self):
    self._buffer = ''

  def isdir(self):
    return False

  @property
  def path(self):
    # TODO: Create a real temporary file and return its path.
    raise Exception('Not implemented')

  def write(self, data):
    self._buffer = data

  def read(self):
    return self._buffer

  def append(self, data):
    self._buffer += data


