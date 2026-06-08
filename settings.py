import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# Diccionarios de configuración global de color solicitados
PALETTES = {
    "azul": {
        "bg_start": "#0C3E3D",      # El azul profundo
        "bg_end": "#000101",        # El fondo oscuro puro
        "text_main": "#DAC6B6",     # Carne claro
        "text_accent": "#C0A088",   # Carne medio
        "text_muted": "#9A7C65",    # Carne oscuro
        "card_bg": "rgba(12, 62, 61, 0.25)",
        "car_image": "auto_azul.png" 
    },
    "rojo": {
        "bg_start": "#800C1F",      # Rojo vibrante oscuro
        "bg_end": "#3C0007",        # Rojo profundo casi negro
        "text_main": "#929CAA",     # Gris claro azulado
        "text_accent": "#7598B9",   # Azul claro brillante
        "text_muted": "#5C7896",    # Azul grisáceo medio
        "card_bg": "rgba(32, 45, 54, 0.4)", 
        "car_image": "auto_rojo.png"
    },
    "verde": {
        "bg_start": "#363F37",      # Verde medio
        "bg_end": "#1F2B27",        # Verde oscuro
        "text_main": "#C0A889",     # Tono café/crema claro
        "text_accent": "#7A4E39",   # Café tierra
        "text_muted": "#536D5F",    # Verde apagado
        "card_bg": "rgba(54, 63, 55, 0.3)",
        "car_image": "auto_verde.png"
    },
    "cyber_dark": {                 # Paleta negra/amarilla
        "bg_start": "#312D2D",      # Gris/Negro industrial
        "bg_end": "#190F0A",        # Negro con matiz cálido
        "text_main": "#EFB17F",     # Amarillo/Naranja brillante
        "text_accent": "#B79479",   # Café dorado
        "text_muted": "rgba(239, 177, 127, 0.6)",
        "card_bg": "rgba(49, 45, 45, 0.35)",
        "car_image": "auto_cyber.png"
    }
}

CURRENT_PALETTE = "azul"

class SettingsPage(Gtk.Box):
    def __init__(self, main_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.get_style_context().add_class("glass")
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.set_margin_top(40)
        self.set_margin_bottom(40)
        self.set_margin_start(40)
        self.set_margin_end(40)  

        self.main_window = main_window # Referencia a car_interface para poder cambiar sus colores
        
        # Título (Cambiamos el emoji de engranaje por texto limpio)
        title = Gtk.Label(label="Ajustes del Sistema")
        title.get_style_context().add_class("temp-huge") # Reutilizamos el estilo de letra grande del clima
        title.set_halign(Gtk.Align.START)
        self.add(title)

        # ── SECCIÓN 1: TEMAS DE COLOR ──
        lbl_colors = Gtk.Label(label="Paleta de Colores")
        lbl_colors.get_style_context().add_class("song-title-huge")
        lbl_colors.set_halign(Gtk.Align.START)
        self.add(lbl_colors)
        box_colors = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
       
        # 1. Botón Azul (Ahora apunta a "azul")
        btn_ocean = Gtk.Button(label="Azul")
        btn_ocean.get_style_context().add_class("settings-btn")
        btn_ocean.connect("clicked", lambda x: self.main_window.apply_dynamic_theme("azul"))    

        # 2. Botón Rojo (Ahora apunta a "rojo")
        btn_crimson = Gtk.Button(label="Rojo")
        btn_crimson.get_style_context().add_class("settings-btn")
        btn_crimson.connect("clicked", lambda x: self.main_window.apply_dynamic_theme("rojo"))     

        # 3. Botón Verde (Ahora apunta a "verde")
        btn_emerald = Gtk.Button(label="Verde")
        btn_emerald.get_style_context().add_class("settings-btn")
        btn_emerald.connect("clicked", lambda x: self.main_window.apply_dynamic_theme("verde"))

        # 4. NUEVO BOTÓN: Cyber Dark (Apunta a "cyber_dark")
        btn_cyber = Gtk.Button(label="Cyber Dark")
        btn_cyber.get_style_context().add_class("settings-btn")
        btn_cyber.connect("clicked", lambda x: self.main_window.apply_dynamic_theme("cyber_dark"))
        
        box_colors.add(btn_ocean)
        box_colors.add(btn_crimson)
        box_colors.add(btn_emerald)
        box_colors.add(btn_cyber) # Agregamos el nuevo botón a la caja
        self.add(box_colors)

        # ── SECCIÓN 2: ESTILO DE ICONOS ──
        lbl_icons = Gtk.Label(label="Estilo de Iconos (Barra Lateral)")
        lbl_icons.get_style_context().add_class("song-title-huge")
        lbl_icons.set_halign(Gtk.Align.START)
        lbl_icons.set_margin_top(20)
        self.add(lbl_icons)
        
        box_icons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)     

        # Primer botón cambiado a "Lineal"
        btn_icon_1 = Gtk.Button(label="Lineal")
        btn_icon_1.get_style_context().add_class("settings-btn")
        btn_icon_1.connect("clicked", lambda x: self.main_window.apply_icons("lineal"))
        
        # Segundo botón cambiado a "Relleno"
        btn_icon_2 = Gtk.Button(label="Relleno")
        btn_icon_2.get_style_context().add_class("settings-btn")
        btn_icon_2.connect("clicked", lambda x: self.main_window.apply_icons("relleno"))
        
        box_icons.add(btn_icon_1)
        box_icons.add(btn_icon_2)
        self.add(box_icons)

        
