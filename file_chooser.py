import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import cairo
import imageio
import numpy as np

DEFAULT_DEPTH = 8

INFO_DEPTH = {
    12: {'dtype': np.uint16, 'mask': 0xfff},
    10: {'dtype': np.uint16, 'mask': 0x3ff},
    8: {'dtype': np.uint8,'mask': 0x3ff}
}
CAIRO_FORMAT = {
    32: cairo.FORMAT_ARGB32, 
    10: cairo.FORMAT_RGB30,
    8: cairo.FORMAT_RGB24
}

class FileChooserWindow(Gtk.Window):

    def __init__(self):
        self.depth=10
        self._mask = INFO_DEPTH[self.depth]['mask']

        Gtk.Window.__init__(self, title="FileChooser Example")

        box = Gtk.Box(spacing=6)
        self.add(box)
        
        self._painter = Gtk.DrawingArea()
        self.add(self._painter)
        self.connect('window-state-event', self._window_state)

        self._image = np.zeros((0, 0), dtype=np.uint32)

        button1 = Gtk.Button("Choose File")
        button1.connect("clicked", self.on_file_clicked)
        box.add(button1)

        # button2 = Gtk.Button("Choose Folder")
        # button2.connect("clicked", self.on_folder_clicked)
        # box.add(button2)

        self._painter.connect('draw', self._draw_on)
        self._draw()
        
    def _window_state(self, widget, event):
        self.is_fullscreen = bool(Gdk.WindowState.FULLSCREEN & event.new_window_state)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            image_path = dialog.get_filename()
            
            img = imageio.imread(image_path)
            self._image = img
            self._draw()

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def _draw(self):
        self._painter.queue_draw()
        self._update()
 
    def _draw_on(self, widget, ctx):
        """ Draw the image using cairo"""
        if self._image.ndim > 2: 
            h, w, d = self._image.shape
        else:
             h, w = self._image.shape
                
        img = np.zeros((h, w), dtype=np.uint32)
        
 
        img[:, :] = ((self._image[:, :, 0] & self._mask).astype(np.uint32) << (2 * self._depth)) + \
                    ((self._image[:, :, 1] & self._mask).astype(np.uint32) << self._depth) + \
                    (self._image[:, :, 2] & self._mask)

        surface = cairo.ImageSurface.create_for_data(img, CAIRO_FORMAT.get(self._depth), w, h)
 
        ctx.set_source_surface(surface, 0, 0)
        ctx.paint()

    def _update(self):
        while Gtk.events_pending():
            Gtk.main_iteration()

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    # def on_folder_clicked(self, widget):
    #     dialog = Gtk.FileChooserDialog("Please choose a folder", self,
    #         Gtk.FileChooserAction.SELECT_FOLDER,
    #         (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
    #          "Select", Gtk.ResponseType.OK))
    #     dialog.set_default_size(800, 400)

    #     response = dialog.run()
    #     if response == Gtk.ResponseType.OK:
    #         print("Select clicked")
    #         print("Folder selected: " + dialog.get_filename())
    #     elif response == Gtk.ResponseType.CANCEL:
    #         print("Cancel clicked")

    #     dialog.destroy()

win = FileChooserWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
