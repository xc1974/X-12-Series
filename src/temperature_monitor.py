import wmi
import time
from collections import deque

class TemperatureMonitor:
    def __init__(self, history_size=3600):  # 默认保存1小时的数据
        self.history_size = history_size
        self.temperature_history = deque(maxlen=history_size)
        self.w = wmi.WMI()
        
    def get_temperature(self):
        try:
            # 尝试从WMI获取温度信息
            temperature_info = self.w.Win32_TemperatureProbe()
            if temperature_info:
                temp = temperature_info[0].CurrentReading
                self._update_history(temp)
                return temp
                
            # 如果上面的方法失败，尝试从ACPI获取
            temperature_info = self.w.MSAcpi_ThermalZoneTemperature()
            if temperature_info:
                # 转换为摄氏度
                temp = (temperature_info[0].CurrentTemperature / 10.0) - 273.15
                self._update_history(temp)
                return temp
                
        except Exception as e:
            print(f"获取温度失败: {str(e)}")
            
        return 0
        
    def _update_history(self, temperature):
        timestamp = time.time()
        self.temperature_history.append((timestamp, temperature))
        
    def get_history(self):
        return list(self.temperature_history)
        
    def get_average_temperature(self, seconds=60):
        """获取指定时间段内的平均温度"""
        if not self.temperature_history:
            return 0
            
        current_time = time.time()
        recent_temps = [
            temp for timestamp, temp in self.temperature_history
            if current_time - timestamp <= seconds
        ]
        
        if not recent_temps:
            return 0
            
        return sum(recent_temps) / len(recent_temps)
        
    def is_temperature_critical(self, threshold=80):
        """检查温度是否超过临界值"""
        if not self.temperature_history:
            return False
            
        current_temp = self.temperature_history[-1][1]
        return current_temp > threshold 