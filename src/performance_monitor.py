import psutil
import time
import wmi
from collections import deque
import GPUtil
import numpy as np
from datetime import datetime
import os

class PerformanceMonitor:
    def __init__(self):
        self.cpu_history = []
        self.memory_history = []
        self.gpu_history = []
        self.fps_history = []
        self.start_time = time.time()
        self.is_monitoring = False
        self.last_record_time = 0
        self.last_display_time = 0
        self.record_interval = 2  # 记录间隔（秒）
        self.display_interval = 6  # 显示更新间隔（秒）
        
        # 初始化性能监控工具
        self.psutil = psutil
        self.wmi = wmi.WMI()
        self.gpu_util = GPUtil.getGPUs()
        
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
        
    def get_memory_usage(self):
        """Get current memory usage percentage"""
        return psutil.virtual_memory().percent
        
    def get_gpu_usage(self):
        """Get current GPU usage percentage"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                # 获取第一个GPU的使用率
                return gpus[0].load * 100
            return 0
        except Exception as e:
            print(f"Error getting GPU usage: {e}")
            return 0
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.is_monitoring = True
        self.start_time = time.time()
        self.last_record_time = time.time()
        self.last_display_time = time.time()
        self.cpu_history = []
        self.memory_history = []
        self.gpu_history = []
        self.fps_history = []
        
    def stop_monitoring(self):
        """Stop performance monitoring and return collected data"""
        self.is_monitoring = False
        data = self.get_data()
        data['end_time'] = time.time()
        return data
        
    def record_data(self, cpu_percent, memory_percent, gpu_percent):
        """Record performance data"""
        current_time = time.time()
        
        # 检查是否需要记录数据（每2秒）
        if current_time - self.last_record_time >= self.record_interval:
            elapsed_time = current_time - self.start_time
            self.cpu_history.append((elapsed_time, cpu_percent))
            self.memory_history.append((elapsed_time, memory_percent))
            self.gpu_history.append((elapsed_time, gpu_percent))
            self.last_record_time = current_time
            
    def record_fps(self, fps):
        """Record FPS data"""
        current_time = time.time()
        
        # 检查是否需要记录数据（每2秒）
        if current_time - self.last_record_time >= self.record_interval:
            elapsed_time = current_time - self.start_time
            self.fps_history.append((elapsed_time, fps))
            self.last_record_time = current_time
            
    def should_update_display(self):
        """检查是否应该更新显示（每5-7秒）"""
        current_time = time.time()
        if current_time - self.last_display_time >= self.display_interval:
            self.last_display_time = current_time
            return True
        return False
        
    def get_latest_data(self):
        """Get latest data"""
        if not self.cpu_history:
            return {
                'cpu': 0,
                'memory': 0,
                'gpu': 0,
                'fps': 0,
                'peak_values': {
                    'cpu': 0,
                    'memory': 0,
                    'gpu': 0,
                    'fps': 0
                }
            }
            
        latest_cpu = self.cpu_history[-1][1]
        latest_memory = self.memory_history[-1][1]
        latest_gpu = self.gpu_history[-1][1]
        latest_fps = self.fps_history[-1][1] if self.fps_history else 0
        
        return {
            'cpu': latest_cpu,
            'memory': latest_memory,
            'gpu': latest_gpu,
            'fps': latest_fps,
            'peak_values': {
                'cpu': max(x[1] for x in self.cpu_history),
                'memory': max(x[1] for x in self.memory_history),
                'gpu': max(x[1] for x in self.gpu_history),
                'fps': max(x[1] for x in self.fps_history) if self.fps_history else 0
            }
        }
        
    def get_data(self):
        """Get all data for report generation"""
        return {
            'start_time': self.start_time,
            'cpu': self.cpu_history,
            'memory': self.memory_history,
            'gpu': self.gpu_history,
            'fps': self.fps_history
        }
        
    def clear_data(self):
        """Clear historical data"""
        self.cpu_history.clear()
        self.memory_history.clear()
        self.gpu_history.clear()
        self.fps_history.clear()
        self.start_time = time.time()
        self.last_record_time = time.time()
        self.last_display_time = time.time()

    def _get_temperature(self):
        # Try multiple methods to get CPU temperature
        
        # 1. Try psutil first
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current > 0:
                            return float(entry.current)
        except Exception:
            pass
            
        # 2. Try WMI
        try:
            w = wmi.WMI(namespace="root\\WMI")
            temperature_info = w.MSAcpi_ThermalZoneTemperature()
            if temperature_info:
                return float((temperature_info[0].CurrentTemperature / 10.0) - 273.15)
        except Exception:
            pass
            
        # 3. Try reading from file (Linux systems)
        try:
            if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp') as f:
                    temp = int(f.read()) / 1000.0
                    return temp
        except Exception:
            pass
            
        return 45.0  # Return a reasonable default value
            
    def calculate_performance_score(self):
        if not self.cpu_history:
            return 0
            
        # Get recent metrics
        recent_cpu = [x[1] for x in self.cpu_history][-60:]  # Last 60 seconds
        recent_memory = [x[1] for x in self.memory_history][-60:]
        recent_gpu = [x[1] for x in self.gpu_history][-60:] if self.gpu_history else [0]
        
        # Calculate averages
        avg_cpu = sum(recent_cpu) / len(recent_cpu) if recent_cpu else 0
        avg_memory = sum(recent_memory) / len(recent_memory) if recent_memory else 0
        avg_gpu = sum(recent_gpu) / len(recent_gpu) if recent_gpu else 0
        
        # Simple scoring system
        performance_score = max(0, 100 - (avg_cpu * 0.5) - (avg_memory * 0.5))
        
        return performance_score 