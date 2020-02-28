from sweepy.sweep import Sweep # base class
from monochromator import Monochromator # base class
class MonochromatorAdapter(object):
    """Adapter for using Monochromator as a MonoSweep base class.

    Issue
    -----
    Derived class MonoSweep has base classes Monochromator and
    Sweep.

    MonoSweep has initialization args for both of its base
    classes.

    Need Monochromator to pass the initialization args along to
    Sweep, because Sweep is the next class in the MRO.

    Monochromator is not designed with this in mind.

    Solution
    --------
    Adapter adds a super() to the __init__() to pass all the
    initialization args that Monochromator doesn't know about
    along to the next class in the MRO.

    Usage
    -----
    # Define MonoSweep as a class derived from Sweep
    # with an instance of Monochromator as one of its attributes.
    from monochromator import Monochromator
    from sweep import Sweep
    class MonoSweep(MonochromatorAdapter, Sweep):
        pass
    
    # Make an instance of MonoSweep
    import monochromator as mon # to get usb_handle
    with mon.usb.open_monochromator() as mono:
        sweep = MonoSweep(
            usb_handle=mono,
            start_nm=300,
            stop_nm=550,
            step_nm=50
            )
        sweep.mon.filterwheel.set_filter('BLANK')
        sweep.step()

    Purpose
    -------
    Object `sweep` has the usual Sweep attributes:

    >>> for k,v in vars(sweep).items():
    >>>     print(f"{k}={v}")
    in_progress=False
    wavelength_to_start_using_400nm_LPF=420
    wavelength_to_start_using_700nm_LPF=720
    wavelengths=[350, 400, 450, 500, 550]
    start_nm=350
    stop_nm=550
    step_nm=50

    And object `sweep` has the usual Sweep methods:
        sweep.start()
        sweep.step()
        sweep.stop()
        etc.
    But as an instance of derived class MonoSweep,
    object `sweep` also has a `mon` attribute

    >>> # first k,v entry in vars(sweep).items()
    mon=<monochromator.monochromator.Monochromator object at 0x0000004A424A5E10>

    `mon` is an instance of base class Monochromator

    >>> print(type(sweep.mon))
    <class 'monochromator.monochromator.Monochromator'>

    The `usb_handle` is stored with `mon`:
        sweep.mon.usb_handle
    Though there is no reason to ever access this attribute.
    And whatever functions are exposed here:
    It is required  when `sweep` is initialized, and thereafter
    MonoSweep uses it internally wherever needed.

    `sweep` also has access to all the functions in
    Monochromator. And `MonoSweep` exposes wrapped versions of
    these functions.

    The wrapped version hides the need to pass the `usb_handle`
    every time a call is made to control the monochromator.

    Consider this call:

        sweep.mon.filterwheel.set_filter('BLANK')

    vs. calling the function directly:

    import monochromator as mon
    mon.filterwheel.set_filter(usb_handle, 'BLANK')

    (The usb_handle is needed in the second case.)

    This arg passing is noise in an application context. The
    usb_handle is yet another piece in setting up the sweep. If
    I'm doing a sweep, I must know the monochromator's usb
    handle. No reason to require passing this arg all the time!
    """
    def __init__(self, usb_handle, **kwargs):
        self.mon = Monochromator(usb_handle)
        super().__init__(**kwargs)

class MonoSweep(MonochromatorAdapter, Sweep):
    """
    Usage
    -----
    # Make an instance of MonoSweep
    import monochromator as mon # to get usb_handle
    with mon.usb.open_monochromator() as mono:
        sweep = MonoSweep(
            usb_handle=mono,
            start_nm=300,
            stop_nm=550,
            step_nm=50
            )
        # Monochromator is 'open' within the with block
        # Change the monochromator filter
        sweep.mon.filterwheel.set_filter('BLANK')
        # Step monochromator grating to next wavelength in sweep
        sweep.step()

    TODO
    ----
    Expose functions of packages monochromator and sweep, wrapped
    for easy use in application.
    """
    def set_filter(self, filter_name='BLANK'):
        """Convenience for calling mon.filterwheel.set_filter().

        Returns nice response with filter name instead of the raw
        string from the monochromator.

        If set filter is OK, store the new filter value in
        attribute `filter`.

        Handles exception thrown if filter name is unknown.
        """
        try:
            response = self.mon.set_filter(
                filter_name=filter_name
                )
            if response == b'  ok\r\n':
                response = f"Filter set to '{filter_name}'."
                self.filter = filter_name
            else:
                print("Unexpected monochromator response:")
                print(response)
                print(type(response))
                response = f"monochromator response: `{response}`"
        except KeyError:
            response = (
                f"ERROR: unrecognized filter name: '{filter_name}'"
                )
        return response
    def set_nm(self, nm):
        """Convenience for calling monochromator.grating.set_nm().

        Send monochromator command to change the wavelength to `nm`.

        Return
        ------
        Status string suitable for display in the application.

        If monochromator responds OK:
            return wavelength string, e.g.: "Wavelength: 550nm"
            set attribute wavelength to `nm`

        If monochromator does not respond with OK:
            return monochromator's response as a string with preface
            "monochromator response: "
        """
        response = self.mon.set_nm(nm)
        if response == b'  ok\r\n':
            response = f"Wavelength: {nm}nm."
            self.wavelength = nm
        else:
            print("Unexpected monochromator response:")
            print(response)
            print(type(response))
            response = f"monochromator response: `{response}`"
        return response
    def step(self):
        """Step wavelength, return status string.

        Algorithm
        ---------
        Check if filter needs to change.
        Change filter when needed.
        Go to next wavelength and return status string with
        wavelength.
        Check if next_wavelength is stop_nm.
        Change state to 'stop' after stepping to stop_nm.
        """
        # Figure out which filter to use
        ''' --- FILTER WHEEL --- '''
        if self.next_wavelength < self.wavelength_to_start_using_400nm_LPF:
            expect_filter = 'BLANK'
            self.filter_changed = self.next_filter != expect_filter
        elif self.next_wavelength < self.wavelength_to_start_using_700nm_LPF:
            expect_filter = '400nm LPF'
            self.filter_changed = self.next_filter != expect_filter
        else:
            expect_filter = '700nm LPF'
            self.filter_changed = self.next_filter != expect_filter
        # Move the filter if it changed
        if self.filter_changed:
            self.next_filter = expect_filter
            # _cmdoutput(f"Moving filter wheel to {self.next_filter}...")
            # '''TODO: make this visible in GUI somehow'''
            # status = (f"Loading filter: {self.next_filter}...")
            '''For now, put on command line'''
            print(f"Loading filter: {self.next_filter}...")
            response = self.set_filter(self.next_filter)
            # _cmdoutput(response + f' Going to {self.next_wavelength}nm...')
        # Step to the next wavelength
        ''' ---GRATING--- '''
        self.set_nm(self.next_wavelength)
        status = (f"Filter: {self.next_filter}, Wavelength: {self.next_wavelength}nm")
        ''' ---INCREMENT AND STOP WHEN DONE--- '''
        if self.next_wavelength > self.stop_nm:
            # Clear flag self.in_progress,
            # restore pre-sweep settings
            self.stop()
            # Move filterwheel back to pre-sweep filter
            print(f"Loading filter: {self.next_filter}...")
            self.set_filter(self.next_filter)
            status = self.set_nm(self.next_wavelength)
        else: self.next_wavelength += self.step_nm
        return status
