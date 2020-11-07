
========
FITSutil
========

FITS tools written in Python:

- `fitstab.py` : Preview a FITS table from the terminal.
- `fits_input.py` : Flexible loading of spectral data, accepts many different formats

FitsTab
-------

The script `fitstab.py` takes the following two arguments::

    python3  fitstab.py  filename.fits  [--ext EXT] [--num NUM]

where `filename.fits` is the FITS Table filename and the optional
`EXT` refers to the extension if there are several TableHDUs in the
FITS file. The optional argument `NUM` refers to the number of rows
to preview, the default value is 10.

Load Spectrum
-------------

The function `fits_input.load_spectrum` takes one argument: the filename
to be searched for spectral data. The function returns the wavelength,
flux, error and mask arrays of 1-dimensional data. The `mask` array is a boolean
pixel mask: `True` if the pixel is 'good', `False` if the pixel is bad and should be ignored.

The following formats are allowed:

- Multi Extension ImageHDUs::

      No.    Name      Ver    Type      Cards   Dimensions   Format
        0  FLUX          1 PrimaryHDU     557   (12854,)   float32
        1  ERRS          1 ImageHDU        23   (12854,)   float32
        2  QUAL          1 ImageHDU        23   (12854,)   int32


- FITS Tabular data::

      No.    Name      Ver    Type      Cards   Dimensions   Format
        0  PRIMARY       1 PrimaryHDU       4   ()
        1  BLUE          1 BinTableHDU     22   46725R x 3C   [D, D, D]
        2  RED           1 BinTableHDU     22   65588R x 3C   [D, D, D]

  -- Note: If more than one extension, only the first extension will be read
  and a UserWarning will be thrown.


- IRAF format::

      No.    Name      Ver    Type      Cards   Dimensions   Format
        0  PRIMARY       1 PrimaryHDU     215   (3141, 1, 4)   float32

  -- Note: If more than one object is present (second dimension > 1),
  only the first object will be read and a UserWarning will be thrown.



Dependencies
------------

Python version 2.7 or >3.6 (tested on 3.7 and 3.8).

Depends on ``astropy`` and ``numpy``.


Setup
-----

To use `fitstab` from the terminal, you can define an alias in your `.bashrc` file (or similar):

.. code-block:: bash

    alias fitstab="python3 /PATH/TO/FITSUTIL/fitstab.py"
