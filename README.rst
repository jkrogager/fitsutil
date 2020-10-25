
========
FITSutil
========

FITS tools written in Python:

- `fitstab.py` : Preview a FITS table from the terminal.

The script `fitstab.py` takes the following two arguments::

    python3  fitstab.py  filename.fits  [--ext EXT] [--num NUM]

where `filename.fits` is the FITS Table filename and the optional
`EXT` refers to the extension if there are several TableHDUs in the
FITS file. The optional argument `NUM` refers to the number of rows
to preview, the default value is 10.


Installation
============

Dependencies
------------

Python version 2.7 or >3.6 (tested on 3.7 and 3.8).

Depends on ``astropy`` and ``numpy``.


Setup
-----

The setup is very simple: Simply add an `alias` in your `.bashrc` file (or similar):

.. code-block:: bash

    alias fitstab="python3 /PATH/TO/FITSUTIL/fitstab.py"

