import os

from . import action, File
from . import util

@action
def build(source_dir, build_path, static_file_paths, file_contents):
  build_files = []
  build_files.extend(util.copy_files(source_dir, build_path,
                                     static_file_paths))

  for file_path, data in file_contents.items():
    f = File(os.path.join(build_path, file_path))
    f.write(data)
    build_files.append(f)

  build_dir = util.delete_unlisted_files(build_path, build_files)
  build_archive = util.create_archive(build_dir)
  return build_dir, build_archive


class Builder(object):
  def __init__(self, source_dir, build_path):
    self.source_dir = source_dir
    self.build_path = build_path
    self.static_file_paths = set()
    self.file_contents = {}

  def copy_files(self, paths):
    self.static_file_paths |= set(paths)

  def copy_file(self, path):
    self.static_file_paths.add(path)

  def write_file(self, file_path, data):
    self.file_contents[file_path] = data

  def build(self):
    return build(self.source_dir, self.build_path, self.static_file_paths,
                 self.file_contents)