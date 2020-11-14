from .fits_input import load_fits_spectrum, FormatError, WavelengthError, load_fits_explicit


def test_fileinput():
    """
    Test if the code can load a set of different spectra with varying formats:
    """

    filelist = [
        ['yes', '/Users/krogager/Projects/eHAQ/Observations/fits_from_johan/flux_eHAQ0001+0233.fits'],
        ['yes', '/Users/krogager/Projects/Q0857_CI/J0857+1855_uves_combined.fits'],
        ['no', '/Users/krogager/Data/ESPRESSO/HE0001-2340/HE0001-2340_1_1d.fits'],
        ['yes', '/Users/krogager/Data/X-shooter/ESDLA2/J0024-0725_2018-08-16_UVB_1d.fits'],
        ['yes', '/Users/krogager/Data/UVES/Q0857+1855/ADP.2013-09-27T18_10_14.790.fits'],
        ['yes', '/Users/krogager/Projects/Q0857_CI/J0857_espresso_combined.fits'],
    ]

    for known_type, fname in filelist:
        try:
            _ = load_fits_spectrum(fname)
            success = 'yes'
        except (FormatError, WavelengthError):
            success = 'no'
        msg = "A spectrum of type %s passed as type %s:  %s" % (known_type, success, fname)
        assert known_type == success, msg


def test_explicit_load():
    """Test the function load_spectrum_explicit"""
    filelist = [
        ['yes', '/Users/krogager/Projects/Q0857_CI/J0857+1855_uves_combined.fits', {'EXT_NUM': 2, 'WAVE': 'WAVELENGTH', 'FLUX': 'FLUX', 'ERR': 'ERR'}, 'inclusion'],
        ['yes', '/Users/krogager/Data/ESPRESSO/HE0001-2340/HE0001-2340_1_1d.fits', {'EXT_NUM': 1, 'WAVE': 'wavelength', 'FLUX': 'flux_cal', 'ERR': 'error_cal'}, 'inclusion'],
        ['yes', '/Users/krogager/Data/X-shooter/ESDLA2/J0024-0725_2018-08-16_UVB_1d.fits', {'EXT_NUM': 0, 'WAVE': 'From FITS Header', 'FLUX': '0', 'ERR': '1', 'MASK': '2'}, 'exclusion'],
        ['no', '/Users/krogager/Data/X-shooter/ESDLA2/J0024-0725_2018-08-16_UVB_1d.fits', {'EXT_NUM': 0, 'WAVE': 'From FITS Header', 'FLUX': '0', 'ERR': 'ERR'}, 'exclusion'],
        ['yes', '/Users/krogager/Data/UVES/Q0857+1855/ADP.2013-09-27T18_10_14.790.fits', {'EXT_NUM': 1, 'WAVE': 'WAVE', 'FLUX': 'FLUX_REDUCED', 'ERR': 'ERR_REDUCED'}, 'inclusion'],
    ]

    passed = list()
    for should_pass, fname, specs, mask_type in filelist:
        try:
            _ = load_fits_explicit(fname, specs, mask_type)
            success = 'yes'
        except (ValueError, IndexError, KeyError, WavelengthError, FormatError):
            success = 'no'
        except:
            success = 'no'

        if success != should_pass:
            print(fname, specs)
        passed.append(success == should_pass)
    assert all(passed)


tmp_var = ["str", "str2", "name"]
tmp_var2 = ["strf", "rupaul", "name"]
def skip_warning():
    """
    The variable list: %(VARS)r
    The other variable list: %(VAR_NAMES)r
    """
    import warnings
    fname = '/Users/krogager/Projects/Q0857_CI/J0857+1855_uves_combined.fits'
    with warnings.catch_warnings(record=True) as w:
        # warnings.simplefilter("ignore")
        # warnings.simplefilter("once")
        try:
            data = load_fits_spectrum(fname)
        except FormatError:
            print("Error: Could not determine the file format.")
            print("       The FITS file has the following structure:")
        print("Number of warnings: %i" % len(w))
skip_warning.__doc__ = skip_warning.__doc__ % {'VARS': tmp_var, 'VAR_NAMES': tmp_var2}

if __name__ == '__main__':
    skip_warning()
    print(skip_warning.__doc__)
