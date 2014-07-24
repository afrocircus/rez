import os
import os.path
from fnmatch import fnmatch
from rez.vendor.argcomplete import CompletionFinder, default_validator, \
    sys_encoding, split_line, debug


class RezCompletionFinder(CompletionFinder):
    def __init__(self, parser, comp_line, comp_point):
        self._parser = parser
        self.always_complete_options = False
        self.exclude = None
        self.validator = default_validator
        self.wordbreaks = " \t\"'@><=;|&(:"  # TODO might need to be configurable/OS specifi

        comp_point = len(comp_line[:comp_point].decode(sys_encoding))
        comp_line = comp_line.decode(sys_encoding)

        cword_prequote, cword_prefix, cword_suffix, comp_words, \
            first_colon_pos = split_line(comp_line, comp_point)

        debug("\nLINE: '{l}'\nPREQUOTE: '{pq}'\nPREFIX: '{p}'".format(l=comp_line, pq=cword_prequote, p=cword_prefix),
              "\nSUFFIX: '{s}'".format(s=cword_suffix),
              "\nWORDS:", comp_words)

        completions = self._get_completions(comp_words, cword_prefix,
                                            cword_prequote, first_colon_pos)
        self.completions = (x.encode(sys_encoding) for x in completions)


def ConfigCompleter(prefix, **kwargs):
    from rez.config import config
    return config.get_completions(prefix)


def PackageCompleter(prefix, **kwargs):
    from rez.packages import get_completions
    c = get_completions(prefix)
    return get_completions(prefix)


class FilesCompleter(object):
    def __init__(self, files=True, dirs=True, file_patterns=None):
        self.files = files
        self.dirs = dirs
        self.file_patterns = file_patterns

    def __call__(self, prefix, **kwargs):
        cwd = os.getcwd()
        abs_ = os.path.isabs(prefix)
        filepath = prefix if abs_ else os.path.join(cwd, prefix)
        n = len(filepath) - len(prefix)
        path, fileprefix = os.path.split(filepath)

        try:
            names = os.listdir(path)
            if not os.path.dirname(prefix):
                names.append(os.curdir)
                names.append(os.pardir)
        except:
            return []

        matching_names = []
        names = (x for x in names if x.startswith(fileprefix))

        for name in names:
            filepath = os.path.join(path, name)
            if os.path.isfile(filepath):
                if not self.files:
                    continue
                if (not self.file_patterns) \
                        or any(fnmatch(name, x) for x in self.file_patterns):
                    matching_names.append(name)
            elif os.path.isdir(filepath):
                matching_names.append(name + os.path.sep)
                if self.dirs:
                    matching_names.append(name)

        if not abs_:
            path = path[n:]
        filepaths = (os.path.join(path, x) for x in matching_names)
        return filepaths