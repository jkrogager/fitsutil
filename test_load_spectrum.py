from fits_input import load_fits_spectrum, FormatError, WavelengthError

def test_fileinput():
    """
    Test if the code can load a set of different spectra with varying formats:
    """

    filelist = {
            'yes': '/Users/krogager/Projects/eHAQ/Observations/fits_from_johan/flux_eHAQ0001+0233.fits',
            'yes': '/Users/krogager/Projects/Q0857_CI/J0857+1855_uves_combined.fits',
            'no':  '/Users/krogager/Data/ESPRESSO/HE0001-2340/HE0001-2340_1_1d.fits',
            'yes': '/Users/krogager/Data/X-shooter/ESDLA2/J0024-0725_2018-08-16_UVB_1d.fits',
            'yes': '/Users/krogager/Data/UVES/Q0857+1855/ADP.2013-09-27T18_10_14.790.fits',
            'yes': '/Users/krogager/Projects/Q0857_CI/J0857_espresso_combined.fits',
            }

    passed = list()
    for known_type, fname in filelist.items():
        try:
            data = load_fits_spectrum(fname)
            success = 'yes'
        except FormatError, WavelengthError:
            success = 'no'
        msg = "A spectrum of type %s passed as type %s:  %s" % (known_type, success, fname)
        assert known_type == success, msg


