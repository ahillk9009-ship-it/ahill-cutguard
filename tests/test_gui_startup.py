import contextlib,io,unittest
from unittest.mock import patch
from cutguard.cli import main

class GuiStartupTests(unittest.TestCase):
    def test_unavailable_display_is_actionable_error(self):
        try: import tkinter
        except ImportError:
            self.skipTest('Tkinter not installed; GUI gate still required')
        err=io.StringIO()
        with patch('tkinter.Tk',side_effect=tkinter.TclError('no display')),contextlib.redirect_stderr(err):
            code=main(['gui'])
        self.assertEqual(code,2)
        self.assertIn('scan',err.getvalue())
        self.assertNotIn('Traceback',err.getvalue())
