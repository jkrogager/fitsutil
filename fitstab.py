
import sys
import os

from astropy.io import fits
from astropy.table import Table

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


def format_table_coldef(coldef):
    """Format the Column Definition of FITS table"""
    window_width = int(subprocess.check_output(shlex.split('tput cols')))
    col_names = coldef.names
    max_name = max([len(name) for name in col_names])
    max_name = max(4, max_name)
    col_formats = list(map(col_format, coldef))
    max_format = max([len(fmt) for fmt in col_formats])
    max_format = max(6, max_format)

    # Determine if the information fits in two columns:
    midpoint = len(col_names)//2
    col_names1 = col_names[:midpoint]
    col_names2 = col_names[midpoint:]
    col_formats1 = col_formats[:midpoint]
    col_formats2 = col_formats[midpoint:]
    max_name1 = max([len(name) for name in col_names1])
    max_name1 = max(4, max_name1)
    max_name2 = max([len(name) for name in col_names2])
    max_name2 = max(4, max_name2)
    max_format1 = max([len(fmt) for fmt in col_formats1])
    max_format1 = max(4, max_format1)
    max_format2 = max([len(fmt) for fmt in col_formats2])
    max_format2 = max(4, max_format2)
    fits_in_2col = (max_name1 + max_format1 + max_name2 + max_format2 + 9) <= window_width
    if (len(coldef) <= 10) or (fits_in_2col is False):
        # Single Column View
        column_overview = ""
        formatter_name = f"{{:>{max_name}}}"
        header_name = f"{{:^{max_name}}}".format("NAME")
        formatter_fmt = f"{{:{max_format}}}"
        header_fmt = f"{{:^{max_format}}}".format("FORMAT")
        column_overview += (max_name + max_format + 5) * "-" + "\n"
        column_overview += f"  {header_name}   {header_fmt}\n"
        column_overview += (max_name + max_format + 5) * "-" + "\n"
        for cn, cf in zip(col_names, col_formats):
            this_line = "  " + formatter_name.format(cn) + " : " + formatter_fmt.format(cf) + "\n"
            column_overview += this_line
        column_overview += (max_name + max_format + 5) * "-" + "\n"
    else:
        # Display in two Columns:
        output_rows = list()
        for cn, cf in zip(col_names1, col_formats1):
            this_row = "  " + ("{:>%i}" % max_name1).format(cn) + " : " + ("{:%i}" % max_format1).format(cf)
            output_rows.append(this_row)
        for num, (cn, cf) in enumerate(zip(col_names2, col_formats2)):
            this_row = '   |   ' + ("{:>%i}" % max_name2).format(cn) + " : " + ("{:%i}" % max_format2).format(cf) + "\n"
            output_rows[num] += this_row
        column_overview = ""
        column_overview += (max_name1 + max_format1 + max_name2 + max_format2 + 9 + 6) * "-" + "\n"
        column_overview += "  " + ("{:^%i}" % max_name1).format('NAME') + '   '
        column_overview += ("{:^%i}" % max_format1).format('FORMAT') + '   |   '
        column_overview += ("{:^%i}" % max_name2).format('NAME') + '   '
        column_overview += ("{:^%i}" % max_format2).format('FORMAT') + "\n"
        column_overview += (max_name1 + max_format1 + max_name2 + max_format2 + 9 + 6) * "-" + "\n"
        for row in output_rows:
            column_overview += row
        column_overview += (max_name1 + max_format1 + max_name2 + max_format2 + 9 + 6) * "-" + "\n"

    return column_overview


def show_table(fname, ext=1):
    """
    Show the top 10 rows of a FITS table using Astropy
    """
    if not os.path.exists(fname):
        print(f" [ERROR] - File not found: {fname}")
        return -1

    fits_table = fits.getdata(fname, ext)
    table = Table(fits_table)
    N_rows = len(table)

    str_repr = table.__repr__()
    all_lines = str_repr.split('\n')
    top10 = all_lines[1:14]
    top10_str = '\n'.join(top10)
    table_format_overview = format_table_coldef(fits_table.columns)
    padding = (len(all_lines[4]) - 17) * "-"
    print(table_format_overview)
    print("---- Top 10 Rows " + padding)
    print(top10_str)
    print("\nLength: %i rows\n" % N_rows)

if __name__ == '__main__':
    fname = sys.argv[1]
    if len(sys.argv) > 2:
        ext = int(sys.argv[2])
    else:
        ext = 1
    show_table(fname, ext)
