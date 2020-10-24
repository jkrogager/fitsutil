
import os

from astropy.io import fits
from astropy.table import Table
import numpy as np

import subprocess
import shlex


FITS_to_string = {'L': 'bool',
                  'X': 'bit',
                  'B': 'byte',
                  'I': 'int16',
                  'J': 'int32',
                  'K': 'int64',
                  'A': 'str',
                  'E': 'float32',
                  'D': 'float64',
                  'C': 'complex32',
                  'M': 'complex64',
                  'P': 'array32',
                  'Q': 'array64'
                  }

def col_format(column):
    """Convert column format to string representation"""
    # Get the character format representation:
    base_format = [key for key in FITS_to_string.keys() if key in column.format][0]
    if column.format.isalpha():
        # Direct look-up:
        format_string = FITS_to_string[base_format]
        if base_format == 'A':
            # Only one character, so format should be 'character' and not 'string':
            format_string = 'char'
    else:
        # Alphanumeric, get the number:
        num = column.format.strip(base_format)
        if base_format == 'A':
            if num == 1:
                format_string = 'char'
            else:
                format_string = FITS_to_string[base_format] + num
        else:
            if column.dim is None:
                shape = '(%s)' % num
            else:
                shape = column.dim
            format_string = FITS_to_string[base_format] + ':Array%s' % shape

    return format_string

def get_view_grid(col_info, ncol):
    N_data_cols = len(col_info)
    chunk_size = N_data_cols // ncol
    if N_data_cols % ncol > 0:
        chunk_size += 1
    view_columns = list()

    for i in range(0, N_data_cols, chunk_size):
        this_col = col_info[i:i+chunk_size]
        while len(this_col) != chunk_size:
            this_col.append(' : ')
        view_columns.append(this_col)
    view_grid = np.column_stack(view_columns)
    return view_grid


def get_column_info(col):
    """Create string representation of FITS Column format"""
    col_format_str = col_format(col)
    return "%s : %s" % (col.name, col_format_str)


sizeof_numpy_unicode_char = np.dtype('U1').itemsize
def get_dtype_length(a):
    return a.itemsize // sizeof_numpy_unicode_char


def get_column_widths(grid):
    column_lengths = list()
    for this_col in grid.T:
        # Calculate the length of each description item: `name : format`
        # This returns an array of shape (N, 2) where N is the number of rows in one column
        items_length = np.vectorize(lambda x: len(x))([item.split(' : ') for item in this_col])
        # The maximum length of an entry in this column will be:
        max_length = np.sum(np.max(items_length, axis=0)) + 3
        # The minimum length of an entry is set by the length of the header: 'NAME : FORMAT' [len=13]
        max_length = max(13, max_length)
        column_lengths.append(max_length)
    return column_lengths


def grid_format_coldef(coldef, xpad=2, ypad=1):
    """Use a flexible grid to define the column view that fits within the window width"""
    ncol = 1
    col_format_strings = [get_column_info(c) for c in coldef]
    view_grid = get_view_grid(col_format_strings, ncol)
    # Calcualte length of each item in the grid:
    column_widths = get_column_widths(view_grid)
    if len(coldef) <= 11:
        # Use only one column
        pass
    else:
        window_width = int(subprocess.check_output(shlex.split('tput cols')))
        # Calculate the maximum length of a row with this number of columns:
        row_length = np.sum(column_widths) + xpad + 5*(ncol - 1)
        while (row_length < window_width):
            ncol += 1
            view_grid = get_view_grid(col_format_strings, ncol)
            column_widths = get_column_widths(view_grid)
            row_length = np.sum(column_widths) + xpad + 5*(ncol - 1)
        if row_length >= window_width:
            ncol -= 1
            view_grid = get_view_grid(col_format_strings, ncol)
            column_widths = get_column_widths(view_grid)

    # Now we have the final grid that fits in the view.
    # First predict the maximum size of each entry after padding:
    if np.max(column_widths) > get_dtype_length(view_grid):
        # update array dtype to encompass new max size:
        new_size = np.max(column_widths)
        view_grid = view_grid.astype('U%i' % new_size)

    # Time to format the columns one by one to align the entries:
    column_header = list()
    for this_col in view_grid.T:
        # Calculate the length of each description item: `name : format`
        # This returns an array of shape (N, 2) where N is the number of rows in one column
        items_length = np.vectorize(lambda x: len(x))([item.split(' : ') for item in this_col])
        # The maximum length of `name` and `format` entries are then:
        max_name, max_fmt = np.max(items_length, axis=0)
        max_name = max(4, max_name)
        max_fmt = max(6, max_fmt)
        # Add padding to each element to match the max length:
        for num, entry in enumerate(this_col):
            name, format = entry.split(' : ')
            name = (max_name - len(name))*' ' + name
            format = format + (max_fmt - len(format))*' '
            new_entry = f"{name} : {format}"
            this_col[num] = new_entry

        # Write a header with the right length and centered names:
        col_header = f"{{:^{max_name}}} : {{:^{max_fmt}}}".format('NAME', 'FORMAT')
        column_header.append(col_header)

    # Format everything to output string:
    header_row = xpad*' ' + "  |  ".join(column_header)
    dash_line = len(header_row) * '-'
    header = ypad*'\n' + '\n'.join([dash_line, header_row, dash_line]) + '\n'
    body = ""
    for line in view_grid:
        text_row = xpad*' ' + "  |  ".join(line) + '\n'
        body += text_row
    footer = dash_line + '\n' + ypad*'\n'
    return header + body + footer


def show_table(fname, ext=1, num=10):
    """
    Show the top `num` rows of a FITS table using Astropy
    Default is to show top 10 lines.
    """
    if not os.path.exists(fname):
        print(f" [ERROR] - File not found: {fname}")
        return -1

    fits_table = fits.getdata(fname, ext, memmap=True)
    table = Table(fits_table[:num])
    N_rows = len(fits_table)

    str_repr = table[:num].__repr__()
    all_lines = str_repr.split('\n')
    top10 = all_lines[1:]
    top10_str = '\n'.join(top10)
    table_format_overview = grid_format_coldef(fits_table.columns)
    padding = (len(all_lines[2]) - 17) * "-"
    print(table_format_overview)
    if num > 0:
        top_line = "---- Top 10 Rows " + padding
        bottom_line = '-' * len(top_line)
        print(top_line)
        print(top10_str)
        print(bottom_line)
        print("")
    print("  Table Length: %i rows\n" % N_rows)


if __name__ == '__main__':
    from argparse import ArgumentParser
    description = """Preview a FITS table from terminal and display the column definitions"""
    parser = ArgumentParser(description=description)
    parser.add_argument("input", type=str,
                        help="FITS Table file")
    parser.add_argument("--ext", "-e", type=int, default=1,
                        help="Give the number of the extension [see `fitsinfo`]")
    parser.add_argument("--num", "-n", type=int, default=10,
                        help="Number of rows to display [default=10]")
    args = parser.parse_args()
    fname = args.input
    ext = args.ext
    num = args.num

    show_table(fname, ext, num)
