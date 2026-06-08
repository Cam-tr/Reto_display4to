import gi
import sys
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GLib, Gdk, GdkPixbuf

# Inicializar GStreamer
Gst.init(sys.argv)

class CameraWindow(Gtk.Window):
    def __init__(self, parent=None):
        super().__init__(title="Cámara de Reversa")
        self.set_default_size(1024, 600)
        
        # Superponer a la interfaz principal y bloquear fondo
        if parent:
            self.set_transient_for(parent)
            self.set_modal(True)
            
        self.set_decorated(False)
        
        overlay = Gtk.Overlay()
        self.add(overlay)
        
        # ── CAPA 1: VIDEO ──
        self.picture = Gtk.Image()
        self.picture.set_size_request(1024, 600)
        overlay.add(self.picture)
        
        # ── CAPA 2: LÍNEAS VECTORIALES ──
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.draw_lines)
        overlay.add_overlay(self.drawing_area)
        
        # ── CAPA 3: BOTÓN DE CERRAR ──
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.set_valign(Gtk.Align.START)
        btn_box.set_margin_top(20)
        btn_box.set_margin_end(20)
        
        close_btn = Gtk.Button(label="❌ Cerrar Cámara")
        close_btn.get_style_context().add_class("close-cam-btn") # <--- LÍNEA NUEVA
        close_btn.connect("clicked", self.on_close)
        btn_box.add(close_btn)
        overlay.add_overlay(btn_box)
        
        self.apply_css()

        # ── PIPELINES DE VIDEO ──
        if sys.platform == "win32":
            # Usamos ksvideosrc para elegir por índice. 
            # 0 suele ser la laptop, 1 suele ser la cámara USB.
            pipeline_str = "ksvideosrc device-index=1 ! videoconvert ! video/x-raw,format=RGB ! appsink name=sink drop=true max-buffers=1 sync=false"
        else:
            # Pipeline exacto de tu código anterior adaptado a GTK4 para la placa Linux
            pipeline_str = "v4l2src device=/dev/video7 ! image/jpeg,width=1280,height=720,framerate=30/1 ! jpegdec ! videoconvert ! video/x-raw,format=RGB ! appsink name=sink drop=true max-buffers=1 sync=false"
            
        self.pipeline = Gst.parse_launch(pipeline_str)
        self.sink = self.pipeline.get_by_name("sink")
        self.sink.set_property("emit-signals", True)
        self.sink.connect("new-sample", self.on_new_sample)
        
        # AQUÍ SE ENCIENDE LA CÁMARA AL ABRIR LA PESTAÑA
        self.pipeline.set_state(Gst.State.PLAYING)

    def on_new_sample(self, sink):
        # Manda los cuadros de la cámara a la ventana de GTK
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        struct = caps.get_structure(0)
        w, h = struct.get_value("width"), struct.get_value("height")
        
        _, map_info = buf.map(Gst.MapFlags.READ)
        bytes_data = GLib.Bytes.new(map_info.data)
        buf.unmap(map_info)
        
        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(bytes_data, GdkPixbuf.Colorspace.RGB, False, 8, w, h, w * 3)
        GLib.idle_add(self.update_picture, pixbuf)
        return Gst.FlowReturn.OK

    def update_picture(self, pixbuf):
        self.picture.set_from_pixbuf(pixbuf)
        return False

    def draw_lines(self, area, cr):
        # Escala automáticamente las coordenadas de 1280x720 a 1024x600
        cr.scale(0.8, 0.8333)
        
        cr.set_line_cap(1) 
        cr.set_line_join(1)

        # Línea guía gris curva
        cr.set_source_rgba(0.88, 0.88, 0.88, 0.6)
        cr.set_line_width(4)
        cr.move_to(390, 260)
        cr.curve_to(556.6, 220, 723.3, 220, 890, 260)
        cr.stroke()

        # Líneas Verdes
        cr.set_source_rgba(0.0, 1.0, 0.0, 0.85)
        cr.set_line_width(14)
        for path in [[(570, 250), (530, 255)], [(570, 250), (515, 350)], 
                     [(710, 250), (750, 255)], [(710, 250), (765, 350)]]:
            cr.move_to(*path[0]); cr.line_to(*path[1]); cr.stroke()

        # Líneas Amarillas
        cr.set_source_rgba(1.0, 1.0, 0.0, 0.85)
        for path in [[(515, 350), (485, 350)], [(515, 350), (440, 490)],
                     [(765, 350), (795, 350)], [(765, 350), (840, 490)]]:
            cr.move_to(*path[0]); cr.line_to(*path[1]); cr.stroke()

        # Líneas Rojas
        cr.set_source_rgba(1.0, 0.0, 0.0, 0.9)
        cr.set_line_width(16)
        for path in [[(440, 490), (490, 490)], [(440, 490), (320, 700)],
                     [(840, 490), (790, 490)], [(840, 490), (960, 700)]]:
            cr.move_to(*path[0]); cr.line_to(*path[1]); cr.stroke()
        return False

    def on_close(self, btn):
        # AQUÍ SE APAGA LA CÁMARA AL DESTRUIR LA VENTANA
        self.pipeline.set_state(Gst.State.NULL)
        self.destroy()

    def apply_css(self):
        css = b'''
        .close-cam-btn {
            background-image: none;
            background-color: rgba(12, 46, 61, 0.65);
            color: #F9DDCA;
            font-size: 20px;
            font-weight: bold;
            border-radius: 12px;
            padding: 15px 25px;
            border: 1px solid rgba(218, 198, 182, 0.15);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
            transition: all 150ms ease;
        }
        .close-cam-btn:hover { 
            background-image: none;
            background-color: rgba(24, 103, 132, 0.8); 
            border-color: #F9DDCA;
        }
        .close-cam-btn:active { 
            background-image: none;
            background-color: #FF453A;
            color: white;
            border-color: #FF453A;
        }
        '''
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)