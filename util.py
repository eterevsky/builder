import itertools
import os
import re
import shutil
import subprocess

from . import action, File


@action
def delete_unlisted_files(dir_path, files):
  paths_with_parents = set()
  for f in files:
    path = os.path.abspath(f.path)
    while path != '' and path != '/':
      paths_with_parents.add(path)
      path = os.path.dirname(path)

  for subdir_path, dir_names, file_names in os.walk(dir_path, topdown=True):
    for name in itertools.chain(dir_names, file_names):
      path = os.path.abspath(os.path.join(subdir_path, name))
      if path not in paths_with_parents:
        print('Deleting', path)
        if os.path.isdir(path):
          shutil.rmtree(path, ignore_errors=True)
        elif os.path.isfile(path):
          os.remove(path)

  return File(dir_path)


_GIT_DESCRIBE_RE = re.compile(r'v?(\d+(?:\.\d+))(?:-(\d+)-g.*)?')

@action
def get_version_from_git(source_dir):
  """Guess the current version from git revision.

  If there are annotated tags in trunk of the form 'vX.Y' or 'X.Y', the version
  will look like 'X.Y.R', where R is the number of revision since the tagged
  commit. If there are no tags, the version will be 'rR', where R is the total
  number of commits in trunk.
  """
  try:
    describe_str = subprocess.check_output(
        ['git', 'describe'], universal_newlines=True, stderr=subprocess.STDOUT,
        cwd=source_dir.path)
  except FileNotFoundError:
    return ''
  except subprocess.CalledProcessError:
    describe_str = None

  if describe_str is None or describe_str.find('fatal') == 0:
    revision = subprocess.check_output(
        ['git', 'rev-list', 'HEAD', '--count'], universal_newlines=True,
        cwd=source_dir.path)
    return 'r' + revision
  else:
    match = _GIT_DESCRIBE_RE.match(describe_str)
    tag = match.group(1)
    if match.group(2):
      return tag + '.' + match.group(2)
    else:
      return tag


@action
def get_git_branch(source_dir):
  return subprocess.check_output(
      ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], universal_newlines=True,
      cwd=source_dir.path).strip()

@action
def is_git_modified(source_dir):
  return (subprocess.check_output(['git', 'diff']) or
          subprocess.check_output(['git', 'diff', '--cached']))

@action
def create_archive(build_dir, format='zip', manifest=None):
  archive_path = shutil.make_archive(
      build_dir.path, format, root_dir=os.path.join(build_dir.path, '..'),
      base_dir=os.path.basename(build_dir.path))
  return File(archive_path)


@action
def copy_file(src, dest_path):
  out = File(dest_path)
  out.write(src.read(mode='b'), mode='b')
  return out


def copy_files(source_dir, dest_path, file_paths):
  copied_files = []
  for path in file_paths:
    rel_path = os.path.relpath(path, source_dir.path)
    copied_files.append(copy_file(File(rel_path),
                                  os.path.join(dest_path, rel_path)))
  return copied_files


def get_unused_filename(existing_files, filename):
  """Provides filename similar to given, not in the given list.

  If filename is /path/to/file.ext, then either it is returned unchanged if it
  is not found in existing_files, or a new path is returned looking like
  /path/to/file13.ext.

  Args:
    existing_files: the list of either paths, of File objects
    filename: the preferred file path to use
  """
  def check(path):
    for existing in existing_files:
      if os.path.samefile(path, existing):
        return False
    return True

  if check(filename):
    return filename

  parent, name = os.path.split(path)
  parts = name.split('.')
  if len(parts) > 1:
    base = '.'.join(parts[:-1])
    ext = parts[-1]
  else:
    ext = None

  for i in range(1, 100000):
    if ext is None:
      new_name = name + str(i)
    else:
      new_name = base + str(i) + '.' + ext
    if check(new_name):
      return new_name


def get_build_path_with_version(
    source_dir, base_build_path, name, default_branch='master', suffixes=[]):
  parts = [name]
  branch = get_git_branch(source_dir)
  if branch != default_branch:
    parts.append(branch)
  parts.append(get_version_from_git(source_dir))
  if is_git_modified(source_dir):
    parts.append('mod')
  parts.extend(suffixes)
  return os.path.join(base_build_path, '-'.join(parts))
