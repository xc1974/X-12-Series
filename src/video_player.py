import cv2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QImage, QPixmap, QScreen, QGuiApplication
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
import time
from PyQt6.QtCore import pyqtSignal

class VideoPlayer(QWidget):
    video_ended = pyqtSignal()
    fps_updated = pyqtSignal(float)
    
    def __init__(self, video_path, screen_index=None):
        super().__init__()
        self.video_path = video_path
        self.screen_index = screen_index
        self.init_ui()
        
        # Create FPS monitoring timer
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_fps)
        self.fps_timer.start(1000)  # Update FPS every second
        self.frame_count = 0
        self.last_fps = 0
        
        # Connect media status change signal
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_changed)
        
    def init_ui(self):
        # Set window
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Add screen selection dropdown
        self.screen_combo = QComboBox()
        self.screen_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background: white;
                min-width: 200px;
            }
        """)
        self.update_screen_list()
        self.screen_combo.currentIndexChanged.connect(self.move_to_screen)
        self.layout.addWidget(self.screen_combo)
        
        # Create video playback component
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)
        
        # Create media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Set media source
        self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
        
        # If screen index is specified, move to that screen
        if self.screen_index is not None and self.screen_index < len(QGuiApplication.screens()):
            self.screen_combo.setCurrentIndex(self.screen_index)
            self.move_to_screen(self.screen_index)
            
        # Double click to toggle fullscreen
        self.video_widget.mouseDoubleClickEvent = self.toggle_fullscreen
        
        # Start playback
        self.media_player.play()
        
    def update_screen_list(self):
        """Update available screen list"""
        self.screen_combo.clear()
        screens = QGuiApplication.screens()
        for i, screen in enumerate(screens):
            geometry = screen.geometry()
            name = screen.name()
            self.screen_combo.addItem(f"Screen {i+1} - {name} ({geometry.width()}x{geometry.height()})")
            
    def move_to_screen(self, index):
        """Move window to specified screen"""
        screens = QGuiApplication.screens()
        if 0 <= index < len(screens):
            screen = screens[index]
            geometry = screen.geometry()
            
            # If in fullscreen mode, need to restore window state first
            if self.isFullScreen():
                self.showNormal()
            
            # Adjust window size to 80% of screen size
            window_width = int(geometry.width() * 0.8)
            window_height = int(geometry.height() * 0.8)
            self.resize(window_width, window_height)
            
            # Move to center of target screen
            self.move(geometry.x() + (geometry.width() - window_width) // 2,
                     geometry.y() + (geometry.height() - window_height) // 2)
                     
    def toggle_fullscreen(self, event):
        """Toggle fullscreen state"""
        if self.isFullScreen():
            self.showNormal()
            self.screen_combo.show()
        else:
            # Get current screen
            current_screen = QGuiApplication.screenAt(self.pos())
            if current_screen:
                self.screen_combo.hide()
                self.showFullScreen()
                # Ensure window is fullscreen on correct screen
                geometry = current_screen.geometry()
                self.setGeometry(geometry)
            
    def update_fps(self):
        """Update FPS count"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            # Get current playback rate as FPS
            current_fps = self.media_player.playbackRate() * 30  # Assuming original video frame rate is 30fps
            self.fps_updated.emit(current_fps)
            
    def handle_media_status_changed(self, status):
        """Handle media status changes"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.video_ended.emit()  # Emit video end signal
            self.fps_timer.stop()  # Stop FPS monitoring
            
    def get_performance_data(self):
        return {
            'current_fps': self.media_player.playbackRate(),
            'target_fps': 30,  # Assuming target frame rate is 30fps
            'frame_times': self.frame_times.copy()
        }
        
    def closeEvent(self, event):
        self.media_player.stop()
        super().closeEvent(event)
        
    def keyPressEvent(self, event):
        """Handle key events"""
        if event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            # ESC key to exit fullscreen
            self.showNormal()
            self.screen_combo.show()
        else:
            super().keyPressEvent(event)

    def update_performance_data(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_frame_time
        
        # Calculate FPS
        frame_time = current_time - self.last_frame_time
        if frame_time > 0:
            fps = 1.0 / frame_time
            self.frame_times.append((elapsed_time, fps))
        self.last_frame_time = current_time
        
        # Get performance data
        cpu_percent = self.performance_monitor.get_cpu_usage()
        memory_percent = self.performance_monitor.get_memory_usage()
        gpu_percent = self.performance_monitor.get_gpu_usage()
        temperature = self.temperature_monitor.get_temperature()
        
        return {
            'cpu': (elapsed_time, cpu_percent),
            'memory': (elapsed_time, memory_percent),
            'gpu': (elapsed_time, gpu_percent),
            'temperature': (elapsed_time, temperature),
            'fps': self.frame_times[-1] if self.frame_times else (elapsed_time, 0),
            'peak_values': {
                'cpu': max(x[1] for x in self.performance_monitor.get_cpu_history()),
                'memory': max(x[1] for x in self.performance_monitor.get_memory_history()),
                'gpu': max(x[1] for x in self.performance_monitor.get_gpu_history()),
                'temperature': max(x[1] for x in self.temperature_monitor.get_temperature_history()),
                'fps': max(x[1] for x in self.frame_times) if self.frame_times else 0
            },
            'start_time': self.last_frame_time,
            'current_time': current_time
        }

    def play_video(self, video_path):
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.media_player.play()
        self.fps_timer.start()  # Start FPS monitoring
        
    def stop_video(self):
        self.media_player.stop()
        self.fps_timer.stop()  # Stop FPS monitoring
        
    def is_playing(self):
        return self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState 