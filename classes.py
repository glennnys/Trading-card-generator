from hmac import new
import tkinter as tk
import tkinter.ttk as ttk

class Limiter(ttk.Scale):

    def __init__(self, *args, **kwargs):
        self.precision = kwargs.pop('precision')  # Remove non-std kwarg.
        self.chain = kwargs.pop('command', lambda *a: None)  # Save if present.
        super(Limiter, self).__init__(*args, command=self._value_changed, **kwargs)

    def _value_changed(self, newvalue):
        oldvalue = float(newvalue)
        newvalue = int(oldvalue)
        if (oldvalue % 10) < 5:
            newvalue += int((10**self.precision)/2)
        if (oldvalue % 10) > 5:
            newvalue -= int((10**self.precision)/2)

        
        # Round to nearest multiple of 10**self.precision.
        newvalue = round(newvalue, -self.precision)

        self.winfo_toplevel().setvar(self.cget('variable'), str(newvalue))
        self.chain(newvalue)  # Call user specified function.