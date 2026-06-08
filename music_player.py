import gi
import os
import urllib.parse
import urllib.request
import sys
from pathlib import Path
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GLib, Gdk

# Inicializar motor de audio
Gst.init(None)

class MusicManager:
    def __init__(self, on_track_change_callback):
        self.callback = on_track_change_callback
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        
        # Reproductor GStreamer para audio
        self.player = Gst.ElementFactory.make("playbin", "audio_player")
        
        if sys.platform == "win32":
            audio_sink = Gst.ElementFactory.make("directsoundsink", "auto_audio")
        if audio_sink:
            self.player.set_property("audio-sink", audio_sink)
        else:
            # En la tarjeta STM32 (Linux) usará el sumidero de audio por defecto (alsasink o pulsesink)
            audio_sink = Gst.ElementFactory.make("alsasink", "auto_audio")
            if audio_sink:
                self.player.set_property("audio-sink", audio_sink)

        # Bus de eventos (para detectar cuando acaba la canción y pasar a la siguiente)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message::eos", self.on_eos) # End Of Stream
        
        # Contenedor principal de la interfaz de la Playlist
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.main_box.get_style_context().add_class("glass")
        self.main_box.set_halign(Gtk.Align.FILL)
        self.main_box.set_valign(Gtk.Align.FILL)
        
        # Título de la pestaña
        title = Gtk.Label(label="Car Playlist")
        title.get_style_context().add_class("song-title-huge")
        title.set_halign(Gtk.Align.START)
        self.main_box.add(title)
        
        # Área con scroll para la lista de canciones
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.get_style_context().add_class("transparent-scroll")

        self.listbox = Gtk.ListBox()
        self.listbox.get_style_context().add_class("playlist-box")
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.add(self.listbox)
        
        self.main_box.add(scroll)
        self.apply_playlist_css()
        # Cargar las canciones al iniciar
        self.load_songs()

        # Reloj en segundo plano para actualizar la barra de progreso (cada segundo)
        GLib.timeout_add_seconds(1, self.update_position_tick)

    def get_widget(self):
        """Retorna el widget principal para insertarlo en el stack de la UI"""
        return self.main_box

    def load_songs(self):
        """Busca archivos MP3 en la carpeta 'musica' y los añade a la lista"""
        music_dir = Path("musica")
        if not music_dir.exists():
            music_dir.mkdir() # Crea la carpeta si no existe
            
        for file in sorted(music_dir.glob("*.mp3")):
            self.add_song_to_ui(file)

    def add_song_to_ui(self, filepath):
        # Intentar separar "Artista - Cancion.mp3" basado en el nombre del archivo
        filename = filepath.stem
        if "-" in filename:
            parts = filename.split("-", 1)
            artist = parts[0].strip()
            title = parts[1].strip()
        else:
            artist = "Desconocido"
            title = filename

        # Guardar en la lógica interna
        track_index = len(self.playlist)
        self.playlist.append({
            "path": str(filepath.resolve()),
            "title": title,
            "artist": artist,
            "duration": "--:--" # GStreamer lo calcula al reproducir
        })

        # --- DISEÑO DE LA FILA DE LA PLAYLIST ---
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        row.get_style_context().add_class("playlist-row")
        row.set_margin_bottom(10)
        
        # Icono de nota musical
        icon = Gtk.Label(label="♫")
        icon.get_style_context().add_class("art-ico-medium")
        icon.set_size_request(50, -1)
        row.add(icon)
        
        # Textos (Título y Artista)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_hexpand(True)
        
        lbl_title = Gtk.Label(label=title)
        lbl_title.get_style_context().add_class("song-title-big")
        lbl_title.set_halign(Gtk.Align.START)
        
        lbl_artist = Gtk.Label(label=artist)
        lbl_artist.get_style_context().add_class("song-artist-big")
        lbl_artist.set_halign(Gtk.Align.START)
        
        vbox.add(lbl_title)
        vbox.add(lbl_artist)
        row.add(vbox)
        
        # Duración (Fija por ahora)
        lbl_dur = Gtk.Label(label="MP3")
        lbl_dur.get_style_context().add_class("song-artist-big")
        lbl_dur.set_margin_end(20)
        row.add(lbl_dur)
        
        # Botón de Reproducir a la derecha
        btn_play = Gtk.Button(label="▶️")
        btn_play.get_style_context().add_class("ctrl-btn")
        btn_play.connect("clicked", lambda b, idx=track_index: self.play_index(idx))
        row.add(btn_play)
        
        self.listbox.add(row)

    # ── CONTROLES DE REPRODUCCIÓN ──
    def play_index(self, index):
        if not self.playlist: return
        
        self.current_index = index
        track = self.playlist[index]
        
        # Formatear la ruta a URI (file:///C:/...) para que GStreamer la entienda
        filepath = track["path"]
        file_uri = urllib.parse.urljoin("file:", urllib.request.pathname2url(filepath))
        
        self.player.set_state(Gst.State.NULL)
        self.player.set_property("uri", file_uri)
        self.player.set_state(Gst.State.PLAYING)
        
        self.is_playing = True
        
        # Actualizar la interfaz central (en car_interface.py)
        self.callback(track["title"], track["artist"], True)

    def toggle_pause(self):
        if not self.playlist: return
        
        if self.is_playing:
            self.player.set_state(Gst.State.PAUSED)
            self.is_playing = False
        else:
            # Si no hay nada reproduciéndose, empezar la primera
            if self.player.get_state(0).state == Gst.State.NULL:
                self.play_index(self.current_index)
            else:
                self.player.set_state(Gst.State.PLAYING)
                self.is_playing = True
                
        # Actualizar el botón de la UI principal
        track = self.playlist[self.current_index]
        self.callback(track["title"], track["artist"], self.is_playing)

    def next_song(self):
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_index(self.current_index)

    def prev_song(self):
        if not self.playlist: return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_index(self.current_index)

    def on_eos(self, bus, msg):
        """Se activa automáticamente cuando acaba la canción"""
        self.next_song()

    def get_position_and_duration(self):
        """Le pregunta a GStreamer la posición actual y la duración en segundos"""
        if not self.is_playing:
            return 0, 0
            
        # GStreamer trabaja en nanosegundos, los convertimos a segundos
        success, position = self.player.query_position(Gst.Format.TIME)
        if not success: position = 0
        
        success, duration = self.player.query_duration(Gst.Format.TIME)
        if not success: duration = 0
        
        return position // Gst.SECOND, duration // Gst.SECOND

    def update_position_tick(self):
        """Se ejecuta cada segundo para avisarle a la interfaz cómo va la canción"""
        if self.is_playing:
            pos, dur = self.get_position_and_duration()
            if dur > 0:
                # Si car_interface nos dio un método para actualizar la barra, lo llamamos
                # Pasamos: posición actual, duración total, y las versiones en texto bonito "MM:SS"
                pos_str = f"{pos // 60}:{pos % 60:02d}"
                dur_str = f"{dur // 60}:{dur % 60:02d}"
                
                # Buscamos una función extendida en la interfaz principal
                if hasattr(self, "ui_progress_callback"):
                    self.ui_progress_callback(pos, dur, pos_str, dur_str)
        return True # Importante para que el temporizador de GLib siga corriendo

    def set_ui_progress_callback(self, callback):
        """Conecta este reproductor con la barra de progreso visual"""
        self.ui_progress_callback = callback

    def apply_playlist_css(self):
        css = '''
        /* Quitamos el fondo blanco de la caja contenedora principal */
        .playlist-box {
            background-color: rgba(6, 28, 38, 0.4); /* Un azul muy oscuro y 40% traslúcido */
            border-radius: 16px;
            padding: 10px;
        }
        
        /* Modificamos cada fila de canción */
        .playlist-row {
            background-color: rgba(12, 46, 61, 0.4); /* Fondo sutil para cada track */
            border-radius: 12px;
            padding: 12px 20px;
            border: 1px solid rgba(249, 221, 202, 0.05);
            transition: all 200ms ease;
        }
        
        /* Efecto Hover estilo Spotify al pasar el mouse por encima */
        .playlist-row:hover {
            background-color: rgba(24, 103, 132, 0.45);
            border-color: rgba(249, 221, 202, 0.3);
        }
        
        /* Aseguramos que el contenedor de scroll no herede fondos blancos genéricos */
        .transparent-scroll {
            background: transparent;
            background-color: transparent;
        }
        
        /* Forzar colores en los textos para que resalte el color carne (#F9DDCA) */
        .song-title-huge {
            color: #F9DDCA;
            font-weight: bold;
            font-size: 28px;
        }
        .song-title-big {
            color: #FFFFFF;
            font-weight: 600;
            font-size: 18px;
        }
        .song-artist-big {
            color: #F9DDCA;
            opacity: 0.8;
            font-size: 14px;
        }
        '''
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)