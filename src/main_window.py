from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSpinBox, QFileDialog, QProgressBar,
                             QGroupBox, QDialog, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices, QPixmap
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import psutil
import wmi
from video_player import VideoPlayer
from performance_monitor import PerformanceMonitor
from temperature_monitor import TemperatureMonitor
from report_generator import ReportGenerator
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os
from datetime import datetime
import time

# Language dictionaries
ENGLISH = {
    'window_title': "PC Performance Benchmark Tool",
    'control_panel': "Control Panel",
    'select_video': "Select Video File",
    'screen_count': "Screen Count:",
    'start_test': "Start Test",
    'stop_test': "Stop Test",
    'view_last_report': "View Last Report",
    'performance_monitor': "Performance Monitor",
    'current_usage': "Current Usage: {}%",
    'peak': "Peak: {}%",
    'current_temp': "Current Temp: {}°C",
    'peak_temp': "Peak: {}°C",
    'language': "Language",
    'full_report': "Open Full Report",
    'performance_report': "Performance Test Report",
    'open_report': "Open Report",
    'close': "Close",
    'no_video': "No video file selected",
    'current_video': "Current video: {}",
    'warning': "Warning",
    'select_video_first': "Please select a video file first",
    'current_fps': "Current FPS: {}",
    'peak_fps': "Peak FPS: {}"
}

TRADITIONAL_CHINESE = {
    'window_title': "PC效能基準測試工具",
    'control_panel': "控制面板",
    'select_video': "選擇視頻文件",
    'screen_count': "螢幕數量:",
    'start_test': "開始測試",
    'stop_test': "停止測試",
    'view_last_report': "查看上次報告",
    'performance_monitor': "效能監控",
    'current_usage': "當前使用率: {}%",
    'peak': "峰值: {}%",
    'current_temp': "當前溫度: {}°C",
    'peak_temp': "峰值: {}°C",
    'language': "語言",
    'full_report': "開啟完整報告",
    'performance_report': "效能測試報告",
    'open_report': "開啟報告",
    'close': "關閉",
    'no_video': "未選擇視頻文件",
    'current_video': "當前視頻: {}",
    'warning': "警告",
    'select_video_first': "請先選擇視頻文件",
    'current_fps': "當前FPS: {}",
    'peak_fps': "峰值FPS: {}"
}

class PerformanceDialog(QDialog):
    def __init__(self, report_path, lang_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang_dict['performance_report'])
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        figure = plt.figure(figsize=(10, 8))
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        
        btn_layout = QHBoxLayout()
        open_report_btn = QPushButton(lang_dict['full_report'])
        open_report_btn.clicked.connect(lambda: os.startfile(os.path.join(report_path, 'report.html')))
        btn_layout.addWidget(open_report_btn)
        layout.addLayout(btn_layout)
        
        img_path = os.path.join(report_path, 'performance_overview.png')
        img = plt.imread(img_path)
        plt.imshow(img)
        plt.axis('off')
        canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang_dict = ENGLISH  # Default language
        self.setWindowTitle(self.lang_dict['window_title'])
        self.setMinimumSize(1000, 800)
        
        # Initialize components
        self.video_file = ""
        self.players = []
        self.perf_monitor = PerformanceMonitor()
        self.temp_monitor = TemperatureMonitor()
        self.report_generator = ReportGenerator('en')  # Initialize with English
        self.last_report_path = None
        self.peak_fps = 0
        
        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create language selector
        self._create_language_selector(layout)
        # Create control panel
        self._create_control_panel(layout)
        # Create monitor panel
        self._create_monitor_panel(layout)
        
        # Create timers for data recording and display updates
        self.record_timer = QTimer()
        self.display_timer = QTimer()
        
        self.record_timer.timeout.connect(self.record_metrics)
        self.display_timer.timeout.connect(self.update_display)
        
        # Initialize recording state
        self.is_recording = False
        
        # Initialize background music player
        self.bgm_player = QMediaPlayer()
        self.bgm_output = QAudioOutput()
        self.bgm_player.setAudioOutput(self.bgm_output)
        self.bgm_output.setVolume(0.2)  # Set volume to 20%
        
    def _create_language_selector(self, parent_layout):
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(self.lang_dict['language']))
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['English', '繁體中文'])
        self.lang_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_combo)
        
        lang_layout.addStretch()
        parent_layout.addLayout(lang_layout)
        
    def change_language(self, lang):
        if lang == 'English':
            self.lang_dict = ENGLISH
            self.report_generator.set_language('en')
        else:
            self.lang_dict = TRADITIONAL_CHINESE
            self.report_generator.set_language('zh')
        self.update_ui_text()
        
    def update_ui_text(self):
        self.setWindowTitle(self.lang_dict['window_title'])
        self.file_btn.setText(self.lang_dict['select_video'])
        self.start_btn.setText(self.lang_dict['start_test'] if self.start_btn.text() != "Stop Test" 
                             else self.lang_dict['stop_test'])
        self.view_report_btn.setText(self.lang_dict['view_last_report'])
        
    def _create_control_panel(self, parent_layout):
        control_group = QGroupBox(self.lang_dict['control_panel'])
        control_layout = QVBoxLayout()
        
        # First row: file selection and screen count
        first_row = QHBoxLayout()
        
        # File selection
        self.file_btn = QPushButton(self.lang_dict['select_video'])
        self.file_btn.clicked.connect(self.select_video_file)
        first_row.addWidget(self.file_btn)
        
        # Video file label
        self.video_file_label = QLabel(self.lang_dict['no_video'])
        first_row.addWidget(self.video_file_label)
        
        # Screen count selection
        self.screen_count_spin = QSpinBox()
        self.screen_count_spin.setRange(1, 16)
        self.screen_count_spin.setValue(4)
        first_row.addWidget(QLabel(self.lang_dict['screen_count']))
        first_row.addWidget(self.screen_count_spin)
        
        control_layout.addLayout(first_row)
        
        # Second row: buttons
        second_row = QHBoxLayout()
        
        # Start/Stop button
        self.start_btn = QPushButton(self.lang_dict['start_test'])
        self.start_btn.clicked.connect(self.start_benchmark)
        second_row.addWidget(self.start_btn)
        
        # View last report button
        self.view_report_btn = QPushButton(self.lang_dict['view_last_report'])
        self.view_report_btn.clicked.connect(self.show_last_report)
        self.view_report_btn.setEnabled(False)
        second_row.addWidget(self.view_report_btn)
        
        control_layout.addLayout(second_row)
        
        control_group.setLayout(control_layout)
        parent_layout.addWidget(control_group)
        
    def _create_monitor_panel(self, parent_layout):
        monitor_group = QGroupBox(self.lang_dict['performance_monitor'])
        monitor_layout = QVBoxLayout()
        
        # CPU panel
        cpu_group = QGroupBox("CPU")
        cpu_layout = QVBoxLayout()
        self.cpu_label = QLabel(self.lang_dict['current_usage'].format(0))
        self.cpu_peak_label = QLabel(self.lang_dict['peak'].format(0))
        self.cpu_bar = QProgressBar()
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_peak_label)
        cpu_layout.addWidget(self.cpu_bar)
        cpu_group.setLayout(cpu_layout)
        monitor_layout.addWidget(cpu_group)
        
        # Memory panel
        memory_group = QGroupBox("RAM")
        memory_layout = QVBoxLayout()
        self.memory_label = QLabel(self.lang_dict['current_usage'].format(0))
        self.memory_peak_label = QLabel(self.lang_dict['peak'].format(0))
        self.memory_bar = QProgressBar()
        memory_layout.addWidget(self.memory_label)
        memory_layout.addWidget(self.memory_peak_label)
        memory_layout.addWidget(self.memory_bar)
        memory_group.setLayout(memory_layout)
        monitor_layout.addWidget(memory_group)
        
        # GPU panel
        gpu_group = QGroupBox("GPU")
        gpu_layout = QVBoxLayout()
        self.gpu_label = QLabel(self.lang_dict['current_usage'].format(0))
        self.gpu_peak_label = QLabel(self.lang_dict['peak'].format(0))
        self.gpu_bar = QProgressBar()
        gpu_layout.addWidget(self.gpu_label)
        gpu_layout.addWidget(self.gpu_peak_label)
        gpu_layout.addWidget(self.gpu_bar)
        gpu_group.setLayout(gpu_layout)
        monitor_layout.addWidget(gpu_group)
        
        # FPS panel
        fps_group = QGroupBox("FPS")
        fps_layout = QVBoxLayout()
        self.current_fps_label = QLabel("当前FPS: 0")
        self.peak_fps_label = QLabel("峰值FPS: 0")
        self.fps_progress = QProgressBar()
        self.fps_progress.setRange(0, 60)  # 设置FPS进度条范围为0-60
        fps_layout.addWidget(self.current_fps_label)
        fps_layout.addWidget(self.peak_fps_label)
        fps_layout.addWidget(self.fps_progress)
        fps_group.setLayout(fps_layout)
        monitor_layout.addWidget(fps_group)
        
        monitor_group.setLayout(monitor_layout)
        parent_layout.addWidget(monitor_group)
        
    def select_video_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            self.lang_dict['select_video'],
            "",
            "Video Files (*.mp4 *.avi *.mkv);;All Files (*.*)"
        )
        if file_name:
            self.video_file = file_name
            self.video_file_label.setText(self.lang_dict['current_video'].format(os.path.basename(file_name)))
            
    def show_last_report(self):
        if self.last_report_path:
            dialog = PerformanceDialog(self.last_report_path, self.lang_dict, self)
            dialog.exec()
            
    def start_benchmark(self):
        """Start benchmark test"""
        if not self.video_file:
            QMessageBox.warning(self, self.lang_dict['warning'], self.lang_dict['select_video_first'])
            return
            
        if self.start_btn.text() == self.lang_dict['start_test']:
            # Start test
            self.test_start_time = time.time()
            self.is_testing = True
            self.is_recording = True
            
            # Create video player
            self.video_player = VideoPlayer(self.video_file)
            self.video_player.video_ended.connect(self.handle_video_ended)
            self.video_player.fps_updated.connect(self.update_fps)
            self.video_player.show()
            
            # Create performance monitor
            self.perf_monitor = PerformanceMonitor()
            self.perf_monitor.start_monitoring()
            
            # Update UI state
            self.start_btn.setText(self.lang_dict['stop_test'])
            self.view_report_btn.setEnabled(False)
            self.video_file_label.setText(self.lang_dict['current_video'].format(os.path.basename(self.video_file)))
            self.screen_count_spin.setEnabled(False)
            
            # Start timers
            self.record_timer.start(5000)   # Record data every 5 seconds
            self.display_timer.start(10000) # Update display every 10 seconds
        else:
            # Stop test
            self.stop_benchmark()
            
    def stop_benchmark(self):
        """停止基准测试"""
        if not self.is_testing:
            return
            
        # 停止测试
        self.is_testing = False
        self.is_recording = False
        
        # 停止定时器
        self.record_timer.stop()
        self.display_timer.stop()
        
        # 关闭视频播放器
        if hasattr(self, 'video_player'):
            self.video_player.stop_video()
            self.video_player.close()
            self.video_player = None
            
        # 停止性能监视器
        if hasattr(self, 'perf_monitor'):
            data = self.perf_monitor.stop_monitoring()
            self.perf_monitor = None
            
            # 生成报告
            report_dir = self.report_generator.generate_report(data)
            self.last_report_path = report_dir
            
            # 播放背景音乐
            bgm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bgm.mp3')
            if os.path.exists(bgm_path):
                self.bgm_player.setSource(QUrl.fromLocalFile(bgm_path))
                self.bgm_output.setVolume(0.2)  # 设置音量为20%
                self.bgm_player.play()
            
            # 显示性能图表
            self.show_performance_dialog(report_dir)
            
        # 更新UI状态
        self.start_btn.setText(self.lang_dict['start_test'])
        self.view_report_btn.setEnabled(True)
        self.video_file_label.setText(self.lang_dict['no_video'])
        self.screen_count_spin.setEnabled(True)
        
    def show_performance_dialog(self, report_dir):
        """显示性能报告对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle(self.lang_dict['performance_report'])
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # 添加图表
        chart_label = QLabel()
        chart_pixmap = QPixmap(os.path.join(report_dir, 'performance_overview.png'))
        chart_label.setPixmap(chart_pixmap.scaled(780, 400, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(chart_label)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        
        open_report_btn = QPushButton(self.lang_dict['open_report'])
        open_report_btn.clicked.connect(lambda: os.startfile(os.path.join(report_dir, 'report.html')))
        button_layout.addWidget(open_report_btn)
        
        close_btn = QPushButton(self.lang_dict['close'])
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # 连接对话框关闭信号
        dialog.finished.connect(self.handle_report_dialog_closed)
        
        dialog.exec()
        
    def handle_report_dialog_closed(self):
        """处理报告对话框关闭事件"""
        # 停止背景音乐
        if self.bgm_player:
            self.bgm_player.stop()
            
    def open_report(self, report_dir):
        """打开HTML报告"""
        report_path = os.path.join(report_dir, 'report.html')
        if os.path.exists(report_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(report_path))
            
    def record_metrics(self):
        """记录性能数据（每秒调用）"""
        if not self.is_recording:
            return
            
        # 获取性能数据
        cpu_percent = self.perf_monitor.get_cpu_usage()
        memory_percent = self.perf_monitor.get_memory_usage()
        gpu_percent = self.perf_monitor.get_gpu_usage()
        
        # 记录数据
        self.perf_monitor.record_data(cpu_percent, memory_percent, gpu_percent)
        
    def update_display(self):
        """更新界面显示（每10秒调用）"""
        if not self.is_testing:
            return
            
        # 获取最新数据
        latest_data = self.perf_monitor.get_latest_data()
        
        # 更新界面显示
        self.cpu_label.setText(self.lang_dict['current_usage'].format(f"{latest_data['cpu']:.1f}"))
        self.cpu_peak_label.setText(self.lang_dict['peak'].format(f"{latest_data['peak_values']['cpu']:.1f}"))
        self.cpu_bar.setValue(int(latest_data['cpu']))
        
        self.memory_label.setText(self.lang_dict['current_usage'].format(f"{latest_data['memory']:.1f}"))
        self.memory_peak_label.setText(self.lang_dict['peak'].format(f"{latest_data['peak_values']['memory']:.1f}"))
        self.memory_bar.setValue(int(latest_data['memory']))
        
        self.gpu_label.setText(self.lang_dict['current_usage'].format(f"{latest_data['gpu']:.1f}"))
        self.gpu_peak_label.setText(self.lang_dict['peak'].format(f"{latest_data['peak_values']['gpu']:.1f}"))
        self.gpu_bar.setValue(int(latest_data['gpu']))
        
    def handle_video_ended(self):
        """处理视频结束事件"""
        self.stop_benchmark()
        
    def update_fps(self, fps):
        """Update FPS display"""
        if not self.is_testing:
            return
            
        # Update current FPS display
        self.current_fps_label.setText(self.lang_dict['current_fps'].format(f"{fps:.1f}"))
        
        # Update peak FPS
        if fps > self.peak_fps:
            self.peak_fps = fps
            self.peak_fps_label.setText(self.lang_dict['peak_fps'].format(f"{self.peak_fps:.1f}"))
            
        # Update FPS progress bar
        self.fps_progress.setValue(int(fps))
        
        # Record FPS data
        if self.perf_monitor:
            self.perf_monitor.record_fps(fps)
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止背景音乐
        if self.bgm_player:
            self.bgm_player.stop()
        
        # 停止基准测试
        if self.perf_monitor:
            self.stop_benchmark()
        
        event.accept() 