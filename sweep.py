'''Base class for making deriving a class specific to an application.

I do not use this class on its own.
It defines generic sweep parameter setup.
See derived class MonoSweep in `monosweep.py`.
'''
class Sweep(object):
    """
    Example
    -------
    # Create a sweep.
    sweep=Sweep(start_nm=300,stop_nm=1000,step_nm=1)

    Example
    -------
    # Change sweep parameters
    sweep.set_wavelengths(start_nm,stop_nm,step_nm)

    Example
    -------
    # Check if the sweep is in progress
    if sweep.in_progress: sweep.step()
    """
    def __init__(
        self,
        start_nm=350,
        stop_nm=850,
        step_nm=10,
        next_wavelength=550,
        next_filter='BLANK',
        ):
        '''TODO: change nm to good defaults when testing is done.'''
        # constants
        self.wavelength_to_start_using_400nm_LPF = 420
        self.wavelength_to_start_using_700nm_LPF = 720
        # flags
        self.in_progress = False
        self.filter_changed = False
        # values
        self.next_filter = next_filter
        self.next_wavelength = next_wavelength
        # wavelength list
        self.set_wavelengths(start_nm,stop_nm,step_nm)
        # saved values to return to after sweep
        self.save_filter = self.next_filter
        self.save_wavelength = self.next_wavelength
        # current value of wavelength and filter
        self.wavelength = 0 # placeholder: set_nm not called yet
        self.filter = 'UNKNOWN' # placeholder: set_filter not called yet
    def start(self):
        """Flag for outside world: sweep in progress.
        Return a status string.
        """
        # Tell the outside world the sweep is happening.
        self.in_progress = True
        # Save state of monochromator before starting sweep
        self.save_filter = self.next_filter
        self.save_wavelength = self.next_wavelength
        # Set next wavelength to starting wavelength
        self.next_wavelength = self.start_nm
        return (
            "Scan: "
            f"{self.start_nm}nm to "
            f"{self.stop_nm}nm in "
            f"{self.step_nm}nm steps. "
            "Moving filter..."
            )
    def stop(self):
        """Flag for outside world: sweep not in progress."""
        self.in_progress = False
        # Restore state prior to sweep
        self.next_filter = self.save_filter
        self.next_wavelength = self.save_wavelength
    def set_wavelengths(self, start_nm, stop_nm, step_nm):
        """Store sweep parameters and create wavelengths list."""
        self.wavelengths=list(
            range(start_nm,stop_nm+step_nm,step_nm)
            )
        self.start_nm=start_nm
        self.stop_nm=stop_nm
        self.step_nm=step_nm
