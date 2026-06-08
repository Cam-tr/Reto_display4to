import gi
import datetime
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
import stream 
import settings # Archivo de CONFIG
import music_player


ICON_SETS = {
    "minimal": {
        "map": "mark-location-symbolic",
        "music": "audio-x-generic-symbolic",
        "weather": "weather-few-clouds-symbolic",
        "settings": "preferences-system-symbolic"
    },
    "classic": {
        "map": "go-home-symbolic",
        "music": "media-playback-start-symbolic",
        "weather": "applications-science-symbolic",
        "settings": "applications-system-symbolic"
    }
}

class CarPlayUI(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Car Dashboard - Custom Palette")
        self.set_default_size(1024, 600)
        self._current_view = "map"
        
        # Referencias para cambiar iconos dinámicamente
        self.sidebar_icons = {} 
        self.css_provider = Gtk.CssProvider() # Proveedor CSS reutilizable
        
        # Agregamos el provider globalmente a la ventana
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        root.set_margin_top(15)
        root.set_margin_bottom(15)
        root.set_margin_start(15)
        root.set_margin_end(15)
        self.add(root)

        root.add(self.build_sidebar())

        self.main_stack = Gtk.Stack()
        self.main_stack.set_hexpand(True)
        self.main_stack.set_vexpand(True)
        self.main_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.main_stack.set_transition_duration(400)

        self.main_stack.add_named(self.build_map_page(), "map")
        # ── INTEGRACIÓN DEL REPRODUCTOR DE MÚSICA ──
        self.music_sys = music_player.MusicManager(self.update_mini_player)
        # Vinculamos el segundero de GStreamer con nuestra barra visual
        self.music_sys.set_ui_progress_callback(self.update_progress_bar)
        self.main_stack.add_named(self.music_sys.get_widget(), "music")
        self.main_stack.add_named(self.build_weather_page(), "weather")
        
        # AÑADIMOS LA PÁGINA DE SETTINGS DESDE EL ARCHIVO NUEVO
        settings_page = settings.SettingsPage(self)
        self.main_stack.add_named(settings_page, "settings")
        
        root.add(self.main_stack)
        root.add(self.build_right_panel())

        # Cargar tema por defecto
        self.apply_dynamic_theme("azul")
        
        GLib.timeout_add_seconds(1, self.tick)
        self.tick()

    # ── SIDEBAR ───────────────────────────────────────────────────
    def build_sidebar(self):
        sb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        sb.get_style_context().add_class("glass")
        sb.set_size_request(80, -1)
        sb.set_valign(Gtk.Align.FILL)
        # Corrección aquí: Creamos la caja y luego asignamos el margen al estilo GTK3
        top_spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        top_spacer.set_margin_top(10)
        sb.add(top_spacer)
        # El botón de cámara no se guarda en el diccionario porque siempre es el mismo
        apps = [
            ("map", "Navegación"),
            ("music", "Música"),
            ("weather", "Clima"),
        ]
        
        for view, tooltip in apps:
            btn = Gtk.Button()
            img = Gtk.Image.new_from_icon_name(ICON_SETS["minimal"][view], Gtk.IconSize.BUTTON)
            img.set_pixel_size(24)
            
            self.sidebar_icons[view] = img # Guardamos la imagen para cambiarla después
            btn.add(img)
            btn.get_style_context().add_class("side-icon")
            btn.set_tooltip_text(tooltip)
            btn.connect("clicked", self.on_nav, view)
            sb.add(btn)
            
        # Botón de cámara (fijo)
        btn_cam = Gtk.Button()
        img_cam = Gtk.Image.new_from_icon_name("camera-video-symbolic", Gtk.IconSize.BUTTON)
        img_cam.set_pixel_size(28)
        btn_cam.add(img_cam)
        btn_cam.get_style_context().add_class("side-icon")
        btn_cam.set_tooltip_text("Cámara Trasera")
        btn_cam.connect("clicked", self.on_nav, "camera")
        sb.add(btn_cam)

        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        sb.add(spacer)

        # Botón de Ajustes (Abre la pestaña settings)
        btn_settings = Gtk.Button()
        img_settings = Gtk.Image.new_from_icon_name(ICON_SETS["minimal"]["settings"], Gtk.IconSize.BUTTON)
        img_settings.set_pixel_size(28)
        self.sidebar_icons["settings"] = img_settings
        
        btn_settings.add(img_settings)
        btn_settings.get_style_context().add_class("side-icon")
        btn_settings.set_margin_bottom(20)
        btn_settings.connect("clicked", self.on_nav, "settings")
        sb.add(btn_settings)

        return sb

    def on_nav(self, btn, view):
        if view == "camera":
            cam_window = stream.CameraWindow(parent=self)
            cam_window.show_all()
            cam_window.present()
        else:
            self.main_stack.set_visible_child_name(view)
            self._current_view = view

    # ── MÉTODOS PARA ACTUALIZAR COLORES E ICONOS DESDE SETTINGS.PY ──
    def apply_dynamic_theme(self, palette_name):
        """Cambia toda la paleta de colores de la interfaz dinámicamente"""
        from settings import PALETTES
        t = PALETTES[palette_name]
        
        bg_gradient = f"linear-gradient(135deg, {t['bg_start']}, {t['bg_end']})"
        glass_border = "rgba(255, 255, 255, 0.1)"

        css_data = f"""
        window {{ background: {bg_gradient}; }}
        .glass {{
            background-color: {t["card_bg"]};
            border: 1px solid {glass_border};
            border-radius: 28px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        }}

        .playlist-row {{
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 10px 20px;
            border: 1px solid {glass_border};
            transition: all 150ms ease;
        }}
        
        .playlist-row:hover {{
            background-color: {t["text_accent"]};
        }}

        .side-icon {{
            background-image: none; 
            background-color: rgba(255, 255, 255, 0.05); 
            border: 1px solid {glass_border}; 
            border-radius: 20px;
            min-width: 52px; min-height: 52px; 
            color: {t["text_main"]}; 
            transition: all 200ms ease;
        }}
        .side-icon:hover {{ background-image: none; background-color: {t["text_accent"]}; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
        .side-icon:active {{ background-image: none; background-color: {t["text_muted"]}; }}
        
        .clock-time {{ font-size: 56px; font-weight: 800; color: {t["text_main"]}; letter-spacing: -2px; }}
        .clock-date {{ font-size: 15px; color: {t["text_main"]}; font-weight: 500; letter-spacing: 1px; }}
        
        .album-art-medium {{ background: linear-gradient(135deg, {t["text_accent"]}, {t["card_bg"]}); border-radius: 20px; box-shadow: 0 12px 24px rgba(0,0,0,0.5); }}
        .art-ico-medium {{ font-size: 48px; color: {t["text_main"]}; opacity: 0.5; }}
        
        .song-title-big {{ font-size: 18px; font-weight: bold; color: {t["text_main"]}; }}
        .song-artist-big {{ font-size: 13px; color: {t["text_muted"]}; }}
        
        .prog trough {{ background-color: rgba(255, 255, 255, 0.1); border-radius: 4px; min-height: 6px; }}
        .prog highlight {{ background-color: {t["text_muted"]}; border-radius: 4px; }}
        
        .ctrl-btn {{ 
            background-image: none; 
            background-color: {t["card_bg"]}; 
            border: 1px solid {glass_border}; 
            border-radius: 50px; 
            font-size: 18px; 
            color: {t["text_main"]}; 
            min-width: 48px; min-height: 48px; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            transition: all 150ms ease;
        }}
        .ctrl-btn:hover {{ background-image: none; background-color: {t["text_accent"]}; border-color: {t["text_main"]}; }}
        .ctrl-btn:active {{ background-image: none; background-color: {t["text_muted"]}; }}

        .btn-outline {{ background-image: none; background-color: transparent; border: 1px solid {glass_border}; border-radius: 14px; color: {t["text_main"]}; padding: 10px; font-size: 13px; }}
        .btn-outline:hover {{ background-image: none; background-color: rgba(255,255,255,0.1); }}
        
        /* Botones de Settings.py */
        .settings-btn {{
            background-image: none;
            background-color: {t["card_bg"]};
            border: 1px solid {glass_border};
            border-radius: 16px;
            color: {t["text_main"]};
            font-size: 18px;
            font-weight: bold;
            padding: 20px 40px;
            transition: all 150ms ease;
        }}
        .settings-btn:hover {{ background-image: none; background-color: {t["text_accent"]}; }}
        .settings-btn:active {{ background-image: none; background-color: {t["text_muted"]}; }}

        .map-bg-inner {{ background-color: rgba(0, 1, 1, 0.4); border-radius: 16px; }}
        .map-route {{ background-color: {t["text_accent"]}; border-radius: 12px; opacity: 0.9; box-shadow: 0 0 20px {t["text_accent"]}; }}
        .map-car {{ font-size: 26px; color: {t["text_main"]}; text-shadow: 0 4px 10px rgba(0,0,0,0.8); }}
        .floating-pill {{ background-color: {t["card_bg"]}; border-radius: 20px; padding: 16px 20px; border: 1px solid {glass_border}; }}
        .nav-arrow {{ font-size: 28px; color: {t["text_muted"]}; font-weight: bold; }}
        .nav-dist  {{ font-size: 28px; font-weight: bold; color: {t["text_main"]}; }}
        .nav-street {{ font-size: 16px; color: {t["text_muted"]}; font-weight: 600; }}
        
        .album-art-huge {{ background: linear-gradient(135deg, {t["text_accent"]}, {t["card_bg"]}); border-radius: 32px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }}
        .art-ico-huge {{ font-size: 80px; color: {t["text_main"]}; opacity: 0.5; }}
        .song-title-huge {{ font-size: 32px; font-weight: bold; color: {t["text_main"]}; }}
        .song-artist-huge {{ font-size: 20px; color: {t["text_muted"]}; }}
        .temp-huge {{ font-size: 90px; font-weight: 800; color: {t["text_main"]}; }}
        """
        self.css_provider.load_from_data(css_data.encode('utf-8'))
        
        # Aplicar el CSS globalmente
        provider = Gtk.CssProvider()
        provider.load_from_data(css_data)
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            
    

    def apply_icons(self, style_name):
        icons = ICON_SETS[style_name]
        for view_name, image_widget in self.sidebar_icons.items():
            image_widget.set_from_icon_name(icons[view_name], Gtk.IconSize.BUTTON)

    # ── VISTAS CENTRALES ──────────────────────────────────────────
    def build_map_page(self):
        overlay = Gtk.Overlay()
        overlay.get_style_context().add_class("glass")

        bg = Gtk.Box()
        bg.get_style_context().add_class("map-bg-inner")
        bg.set_hexpand(True)
        bg.set_vexpand(True)
        overlay.add(bg)

        route = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        route.get_style_context().add_class("map-route")
        route.set_halign(Gtk.Align.CENTER)
        route.set_valign(Gtk.Align.CENTER)
        route.set_size_request(24, 250)
        overlay.add_overlay(route)

        car = Gtk.Label(label="▲")
        car.get_style_context().add_class("map-car")
        car.set_halign(Gtk.Align.CENTER)
        car.set_valign(Gtk.Align.CENTER)
        overlay.add_overlay(car)

        nav = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        nav.get_style_context().add_class("floating-pill")
        nav.set_valign(Gtk.Align.START)
        nav.set_halign(Gtk.Align.START)
        nav.set_margin_top(24)
        nav.set_margin_start(24)

        arrow_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        arrow_lbl = Gtk.Label(label="↱")
        arrow_lbl.get_style_context().add_class("nav-arrow")
        dist = Gtk.Label(label="150 m")
        dist.get_style_context().add_class("nav-dist")
        arrow_row.add(arrow_lbl)
        arrow_row.add(dist)
        nav.add(arrow_row)

        street = Gtk.Label(label="Av. de la Innovación")
        street.get_style_context().add_class("nav-street")
        street.set_halign(Gtk.Align.START)
        nav.add(street)
        overlay.add_overlay(nav)

        return overlay

    def build_weather_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.get_style_context().add_class("glass")
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.set_hexpand(True)
        box.set_vexpand(True)

        temp_big = Gtk.Label(label="26°C")
        temp_big.get_style_context().add_class("temp-huge")
        box.add(temp_big)
        return box

    # ── PANEL DERECHO Y CONTROLES DE MÚSICA ──────────────────────
    def build_right_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        panel.set_size_request(280, -1)

        clock_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        clock_card.get_style_context().add_class("glass")
        clock_card.set_margin_top(30)
        clock_card.set_margin_bottom(30)
        clock_card.set_margin_start(20)
        clock_card.set_margin_end(20)

        self.lbl_time = Gtk.Label(label="12:00")
        self.lbl_time.get_style_context().add_class("clock-time")
        
        self.lbl_date = Gtk.Label(label="Lunes, 1 Enero")
        self.lbl_date.get_style_context().add_class("clock-date")

        clock_card.add(self.lbl_time)
        clock_card.add(self.lbl_date)
        panel.add(clock_card)

        music_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        music_card.get_style_context().add_class("glass")
        music_card.set_vexpand(True)

        top_music = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        top_music.set_valign(Gtk.Align.CENTER)
        top_music.set_vexpand(True)

        art_box = Gtk.Box()
        art_box.get_style_context().add_class("album-art-medium")
        art_box.set_size_request(130, 130)
        art_box.set_halign(Gtk.Align.CENTER)
        art_lbl = Gtk.Label(label="♪")
        art_lbl.get_style_context().add_class("art-ico-medium")
        art_box.add(art_lbl)
        top_music.add(art_box)

        # Usamos variables self. para poder modificar el texto desde la función de actualización
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.lbl_mini_title = Gtk.Label(label="Esperando...")
        self.lbl_mini_title.get_style_context().add_class("song-title-big")
        self.lbl_mini_artist = Gtk.Label(label="Selecciona una canción")
        self.lbl_mini_artist.get_style_context().add_class("song-artist-big")
        
        text_box.add(self.lbl_mini_title)
        text_box.add(self.lbl_mini_artist)
        top_music.add(text_box)
        
        music_card.add(top_music)

        bottom_music = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Fila horizontal para poner: Tiempo Actual | Barra | Tiempo Total
        progress_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.lbl_time_current = Gtk.Label(label="0:00")
        self.lbl_time_current.get_style_context().add_class("song-artist-big")
        
        # Guardamos la barra en self.prog para poder moverla dinámicamente
        self.prog = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.prog.set_value(0)
        self.prog.set_draw_value(False)
        self.prog.set_hexpand(True)
        self.prog.get_style_context().add_class("prog")
        
        self.lbl_time_total = Gtk.Label(label="0:00")
        self.lbl_time_total.get_style_context().add_class("song-artist-big")
        
        progress_row.add(self.lbl_time_current)
        progress_row.add(self.prog)
        progress_row.add(self.lbl_time_total)
        
        bottom_music.add(progress_row)

        # Controles de reproducción interactivos conectados a music_sys
        ctrl_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        ctrl_row.set_halign(Gtk.Align.CENTER)
        
        btn_prev = Gtk.Button(label="⏮")
        btn_prev.get_style_context().add_class("ctrl-btn")
        btn_prev.connect("clicked", lambda x: self.music_sys.prev_song())
        
        self.btn_play_pause = Gtk.Button(label="▶️")
        self.btn_play_pause.get_style_context().add_class("ctrl-btn")
        self.btn_play_pause.connect("clicked", lambda x: self.music_sys.toggle_pause())
        
        btn_next = Gtk.Button(label="⏭")
        btn_next.get_style_context().add_class("ctrl-btn")
        btn_next.connect("clicked", lambda x: self.music_sys.next_song())
        
        ctrl_row.add(btn_prev)
        ctrl_row.add(self.btn_play_pause)
        ctrl_row.add(btn_next)
        
        bottom_music.add(ctrl_row)
        
        btn_full = Gtk.Button(label="Ver pantalla completa")
        btn_full.get_style_context().add_class("btn-outline")
        btn_full.connect("clicked", self.on_nav, "music")
        bottom_music.add(btn_full)

        music_card.add(bottom_music)
        panel.add(music_card)

        return panel

    def update_mini_player(self, title, artist, is_playing):
        """Actualiza la tarjeta derecha cuando music_player detecta un cambio de canción"""
        self.lbl_mini_title.set_text(title)
        self.lbl_mini_artist.set_text(artist)
        if is_playing:
            self.btn_play_pause.set_label("⏸")
        else:
            self.btn_play_pause.set_label("▶️")

    def update_progress_bar(self, current_sec, total_sec, current_str, total_str):
        """Actualiza la barra de progreso y los textos de tiempo en tiempo real"""
        # Ajustamos el rango máximo de la barra al total de segundos de la canción
        self.prog.set_range(0, total_sec)
        # Movemos el indicador al segundo actual
        self.prog.set_value(current_sec)
        
        # Cambiamos los textos de los lados
        self.lbl_time_current.set_text(current_str)
        self.lbl_time_total.set_text(total_str)

    def tick(self):
        now = datetime.datetime.now()
        self.lbl_time.set_text(now.strftime("%H:%M"))
        dias = ["Dom","Lun","Mar","Mié","Jue","Vie","Sáb"]
        meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        
        weekday_str = dias[(now.weekday() + 1) % 7]
        self.lbl_date.set_text(f"{weekday_str}, {now.day} {meses[now.month-1]}".upper())
        return True

def on_activate(app):
    win = CarPlayUI(app)
    win.show_all()
    win.present()

app = Gtk.Application(application_id="com.dashboard.glass_custom")
app.connect("activate", on_activate)
app.run()
