import os

from . import action, File
from . import util

@action
def build(source_dir, build_path, files_to_copy, file_contents):
  build_files = []
  for dest_path, src_file in files_to_copy.items():
    full_path = os.path.join(build_path, dest_path)
    build_files.append(util.copy_file(src_file, full_path))

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
    self.file_contents = {}
    self.files_to_copy = {}

  def copy_file(self, src, dest_path):
    self.files_to_copy[dest_path] = src

  def copy_file_same_path(self, path):
    self.copy_file(self.source_dir / path, path)

  def copy_files_same_path(self, paths):
    for path in paths:
      self.copy_file_same_path(path)

  def write_file(self, file_path, data):
    self.file_contents[file_path] = data

  def build(self):
    return build(self.source_dir, self.build_path, self.files_to_copy,
                 self.file_contents)
