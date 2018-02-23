#! /usr/bin/env python3

# TODO: What about block comments and docstrings?

import argparse
import fnmatch
import os


class CountResult:
    def __init__(self, lines_count=0, files_count=0, dirs_count=0):
        self.lines_count = lines_count
        self.files_count = files_count
        self.dirs_count = dirs_count

    def add(self, other):
        self.lines_count += other.lines_count
        self.files_count += other.files_count
        self.dirs_count += other.dirs_count

    def __repr__(self):
        return ('Counted %d lines in %d files and %d directories.'
                % (self.lines_count, self.files_count, self.dirs_count))


def file_lines(file, line_filter):
    print('Counting in: %s (file)' % file)
    lines_count = 0
    try:
        with open(file, 'r') as f:
            for line in f:
                stripped = line.strip()
                if line_filter(stripped):
                    lines_count += 1
    except:
        pass
    return lines_count


def recurse_count(dir, dir_filter, file_filter, line_filter):
    result = CountResult()
    for obj in os.listdir(dir):
        obj = os.path.join(dir, obj)
        if os.path.isdir(obj) and dir_filter(obj):
            result.add(recurse_count(obj, dir_filter, file_filter, line_filter))
        elif os.path.isfile(obj) and file_filter(obj):
            result.files_count += 1
            result.lines_count += file_lines(obj, line_filter)

    return result


def count_lines(root_dir, only=None, ignored=None, line_comments=None,
        block_comment_starts=None, block_comment_ends=None, include_hidden=False):
    if not os.path.isdir(root_dir):
        raise TypeError('Passed `root_dir` parameter %s is not a directory!' % root_dir)

    def line_filter(line):
        return len(line) > 0 and not any(line.startswith(lc) for lc in line_comments)

    # Particular filters for file-system objects

    def ignore_filter(file):
        return not any(fnmatch.fnmatch(file, pat) for pat in ignored)

    def only_filter(file):
        return any(fnmatch.fnmatch(file, pat) for pat in only)

    def hidden_filter(file):
        return not os.path.basename(file).startswith('.')

    # Actual filters for files and directories

    base_filters = []

    if not include_hidden:
        base_filters.append(hidden_filter)

    def file_filter(file):
        filters = base_filters.copy()

        if only: filters.append(only_filter)
        if ignored: filters.append(ignore_filter)

        return all(f(file) for f in filters)

    def dir_filter(file):
        filters = base_filters.copy()

        if ignored: filters.append(ignore_filter)

        return all(f(file) for f in filters)

    print(recurse_count(root_dir, dir_filter, file_filter, line_filter))


def main():
    parser = argparse.ArgumentParser(
        prog='lc.py',
        description='Line-counting utility tool - counts the number of source'
                    'code lines in a folder and all it\'s subfolders',
        epilog='For more info, see: https://github.com/zjurelinac/lc',
        add_help=False
    )

    parser.add_argument('root_dir', type=str, default='.', nargs='?',
        help='Root directory from which the counting starts')
    parser.add_argument('-o', '--only', action='append', default=[],
        help='Consider only files matching this pattern')
    parser.add_argument('-i', '--ignore', action='append', default=[],
        help='Ignore files and folders matching this pattern')
    parser.add_argument('-c', '--line-comment', action='append', default=['//'],
        help='Ignore lines starting with this string')
    parser.add_argument('-h', '--include-hidden', action='store_true',
        help='Include hidden files - those whose names start with a \'.\'')
    parser.add_argument('--help', action='help',
        help='Show this help message and exit')

    args = parser.parse_args()

    count_lines(
        args.root_dir,
        only=args.only,
        ignored=args.ignore,
        line_comments=args.line_comment,
        include_hidden=args.include_hidden
    )


if __name__ == '__main__':
    main()
