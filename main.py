import gi
gi.require_version('Gtk', '3.0')  # noqa: disable=E402
from gi.repository import Gtk, Gdk
import cairo
import imageio
import numpy as np
import time
 
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
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

class Viewer(object):
 
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, depth=DEFAULT_DEPTH):
        # self.choose_window = Gtk.Window(title="")
        self._window = Gtk.Window(title="Viewer")
        self.box = Gtk.Box()
        self.btn_file = Gtk.Button('Choose file')
        self.dr_image = Gtk.DrawingArea()
        print(dir(self.dr_image.props))
        self._width = width
        self._height = height
        self._depth = depth
        self._image = np.zeros((height, width), dtype=np.uint32)
        self._mask = INFO_DEPTH[depth]['mask']
        self._dtype = INFO_DEPTH[depth]['dtype']
        self._initUI()
 
    def _initUI(self):
        """Init the Gui"""
        
        self._window.resize(self._width, self._height)
        self._window.add(self.box)
        self.box.add(self.btn_file)
        self.box.add(self.dr_image)
        self.dr_image.set_size_request(self._width,self._height)
        self.btn_file.connect("clicked", self.on_file_clicked)
        # self._window.add(self.dr_image)
        self._window.connect('window-state-event', self._window_state)
 
        cursor = Gdk.Cursor.new(Gdk.CursorType.BLANK_CURSOR)
        self._window.get_root_window().set_cursor(cursor)
        self._window.connect("destroy", self.destroy)
 
        self.dr_image.connect('draw', self._draw_on)
        self._window.show_all()
        self._draw()
         
    def _window_state(self, widget, event):
        self.is_fullscreen = bool(Gdk.WindowState.FULLSCREEN & event.new_window_state)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self._window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            image_path = dialog.get_filename()
            v.display_image(image_path)
            v._update()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)


    @property
    def size(self):
        size = self._window.get_size()
        return size.width, size.height
 
    @size.setter
    def size(self, width, height):
        self._window.resize(width, height)
        self._draw()
        
    @property
    def fullscreen(self):
        return self.is_fullscreen
 
    @fullscreen.setter
    def fullscreen(self, fullscreen):
        if fullscreen:
            self._window.fullscreen()
        else:
            self._window.unfullscreen()
         
    def display_image(self, image):
        img = imageio.imread(image)
        self._image = img
        self._draw()
         
    def _draw(self):
        self.dr_image.queue_draw()
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
 
        ctx.set_source_surface(surface, -1, -1)
        ctx.paint()
         
    def _update(self):
        """ manuel main iteration """
        while Gtk.events_pending():
            Gtk.main_iteration()
 
    def destroy(self):
        try:
            cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
            self._window.get_root_window().set_cursor(cursor)
            self._window.hide()
            Gtk.main_quit()
            self._update()
            
        except AttributeError:
            raise AttributeError("Already destroy")
 
        self.dr_image = None
        self._window = None
        
 
 
if __name__ == '__main__':
    v = Viewer(depth=10)
    # v.display_image('images/C46_HDR.hdr')
    v.display_image('images/Copy_of_library_HDR.tiff')
    v._update()
    Gtk.main()