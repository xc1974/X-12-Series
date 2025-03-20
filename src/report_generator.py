import os
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

class ReportGenerator:
    def __init__(self, language='zh'):
        self.text = {
            'en': {
                'report_title': 'Performance Test Report',
                'test_duration': 'Test Duration',
                'performance_score': 'Performance Score',
                'score_explanation': 'Score Explanation',
                'average': 'Average',
                'peak': 'Peak',
                'min': 'Minimum',
                'overview_chart': 'Performance Overview'
            },
            'zh': {
                'report_title': '性能测试报告',
                'test_duration': '测试时间',
                'performance_score': '性能评分',
                'score_explanation': '评分说明',
                'average': '平均值',
                'peak': '峰值',
                'min': '最小值',
                'overview_chart': '性能概览'
            }
        }[language]

    def generate_report(self, data):
        """生成性能报告
        
        Args:
            data (dict): 包含性能数据的字典，格式为：
                {
                    'cpu': [(timestamp, value), ...],
                    'memory': [(timestamp, value), ...],
                    'gpu': [(timestamp, value), ...],
                    'fps': [(timestamp, value), ...]
                }
        
        Returns:
            str: 报告目录的路径
        """
        # 创建报告目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = os.path.join('reports', f'report_{timestamp}')
        os.makedirs(report_dir, exist_ok=True)
        
        # 生成性能图表
        self._create_performance_chart(data, report_dir)
        
        # 生成HTML报告
        self._create_html_report(data, report_dir)
        
        return report_dir

    def _create_performance_chart(self, data, report_dir):
        """Create performance overview chart"""
        # Extract timestamps and values
        timestamps = [x[0] for x in data['cpu']]
        cpu_values = [x[1] for x in data['cpu']]
        memory_values = [x[1] for x in data['memory']]
        gpu_values = [x[1] for x in data['gpu']]
        fps_values = [x[1] for x in data['fps']] if 'fps' in data else []

        # Print debug information
        print(f"Data points: {len(timestamps)}")
        print(f"CPU values: {len(cpu_values)}")
        print(f"Memory values: {len(memory_values)}")
        print(f"GPU values: {len(gpu_values)}")
        print(f"FPS values: {len(fps_values)}")

        # Create chart
        plt.figure(figsize=(12, 6))
        
        # Plot CPU, Memory and GPU usage
        plt.subplot(2, 1, 1)
        plt.plot(timestamps, cpu_values, label='CPU', color='#2196F3', linewidth=2)
        plt.plot(timestamps, memory_values, label='RAM', color='#4CAF50', linewidth=2)
        if gpu_values:  # Only plot GPU if data exists
            plt.plot(timestamps, gpu_values, label='GPU', color='#FFC107', linewidth=2)
        plt.title('Resource Usage')
        plt.ylabel('Usage (%)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Set y-axis limits for better visibility
        plt.ylim(0, 100)
        
        # Plot FPS
        plt.subplot(2, 1, 2)
        if fps_values and len(fps_values) == len(timestamps):  # Ensure FPS data matches timestamp length
            plt.plot(timestamps, fps_values, label='FPS', color='#E91E63', linewidth=2)
        plt.title('Frame Rate')
        plt.ylabel('FPS')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save chart with higher DPI and better quality
        plt.savefig(os.path.join(report_dir, 'performance_overview.png'), 
                   dpi=300, 
                   bbox_inches='tight',
                   facecolor='white',
                   edgecolor='none')
        plt.close()

    def _create_html_report(self, data, report_dir):
        """Create HTML report"""
        # Extract performance data values (values only, no timestamps)
        cpu_values = [x[1] for x in data['cpu']]
        memory_values = [x[1] for x in data['memory']]
        gpu_values = [x[1] for x in data['gpu']]
        fps_values = [x[1] for x in data['fps']] if 'fps' in data else []
        
        # Calculate statistics
        cpu_stats = {
            'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            'peak': max(cpu_values) if cpu_values else 0,
            'min': min(cpu_values) if cpu_values else 0
        }
        
        memory_stats = {
            'average': sum(memory_values) / len(memory_values) if memory_values else 0,
            'peak': max(memory_values) if memory_values else 0,
            'min': min(memory_values) if memory_values else 0
        }
        
        gpu_stats = {
            'average': sum(gpu_values) / len(gpu_values) if gpu_values else 0,
            'peak': max(gpu_values) if gpu_values else 0,
            'min': min(gpu_values) if gpu_values else 0
        }
        
        fps_stats = {
            'average': sum(fps_values) / len(fps_values) if fps_values else 0,
            'peak': max(fps_values) if fps_values else 0,
            'min': min(fps_values) if fps_values else 0
        }
        
        # Calculate performance score
        stats = {
            'cpu': {'values': cpu_values, 'stats': cpu_stats},
            'memory': {'values': memory_values, 'stats': memory_stats},
            'gpu': {'values': gpu_values, 'stats': gpu_stats}
        }
        performance_score = self.calculate_performance_score(stats, fps_values)
        
        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.text['report_title']}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f8f9fa;
                    height: 100vh;
                    box-sizing: border-box;
                    color: #2c3e50;
                }}
                .container {{
                    max-width: 1600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    padding: 20px;
                    height: calc(100vh - 40px);
                    display: grid;
                    grid-template-rows: auto 1fr;
                    gap: 20px;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding-bottom: 15px;
                    border-bottom: 2px solid #eee;
                }}
                .header-left h1 {{
                    margin: 0;
                    font-size: 24px;
                    color: #1a237e;
                }}
                .header-right {{
                    text-align: right;
                    font-size: 14px;
                    color: #666;
                }}
                .content {{
                    display: grid;
                    grid-template-columns: 350px 1fr;
                    gap: 20px;
                    height: 100%;
                }}
                .stats-panel {{
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }}
                .stat-box {{
                    background: white;
                    border-radius: 6px;
                    padding: 15px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                }}
                .stat-box h2 {{
                    margin: 0 0 10px 0;
                    font-size: 16px;
                    color: #1a237e;
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }}
                .stat-box p {{
                    margin: 5px 0;
                    font-size: 14px;
                    display: flex;
                    justify-content: space-between;
                }}
                .value {{
                    font-weight: 500;
                    color: #2196F3;
                }}
                .peak {{
                    color: #f44336;
                }}
                .min {{
                    color: #4caf50;
                }}
                .score-box {{
                    text-align: center;
                    padding: 20px;
                    background: #1a237e;
                    color: white;
                    border-radius: 6px;
                    margin-bottom: 10px;
                }}
                .score-value {{
                    font-size: 36px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .score-text {{
                    font-size: 14px;
                    opacity: 0.9;
                }}
                .charts-panel {{
                    display: grid;
                    grid-template-rows: 1fr 1fr;
                    gap: 15px;
                }}
                .chart-container {{
                    background: white;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                }}
                .chart-container h2 {{
                    margin: 0 0 10px 0;
                    font-size: 16px;
                    color: #1a237e;
                }}
                img {{
                    width: 100%;
                    height: calc(100% - 30px);
                    object-fit: contain;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="header-left">
                        <h1>{self.text['report_title']}</h1>
                    </div>
                    <div class="header-right">
                        <p>{self.text['test_duration']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
                
                <div class="content">
                    <div class="stats-panel">
                        <div class="score-box">
                            <div class="score-text">{self.text['performance_score']}</div>
                            <div class="score-value">{performance_score}</div>
                            <div class="score-text">{self.text['score_explanation']}</div>
                        </div>
                        
                        <div class="stat-box">
                            <h2>📊 CPU</h2>
                            <p>{self.text['average']}: <span class="value">{cpu_stats['average']:.1f}%</span></p>
                            <p>{self.text['peak']}: <span class="value peak">{cpu_stats['peak']:.1f}%</span></p>
                            <p>{self.text['min']}: <span class="value min">{cpu_stats['min']:.1f}%</span></p>
                        </div>
                        <div class="stat-box">
                            <h2>💾 RAM</h2>
                            <p>{self.text['average']}: <span class="value">{memory_stats['average']:.1f}%</span></p>
                            <p>{self.text['peak']}: <span class="value peak">{memory_stats['peak']:.1f}%</span></p>
                            <p>{self.text['min']}: <span class="value min">{memory_stats['min']:.1f}%</span></p>
                        </div>
                        <div class="stat-box">
                            <h2>🎮 GPU</h2>
                            <p>{self.text['average']}: <span class="value">{gpu_stats['average']:.1f}%</span></p>
                            <p>{self.text['peak']}: <span class="value peak">{gpu_stats['peak']:.1f}%</span></p>
                            <p>{self.text['min']}: <span class="value min">{gpu_stats['min']:.1f}%</span></p>
                        </div>
                        <div class="stat-box">
                            <h2>🎯 FPS</h2>
                            <p>{self.text['average']}: <span class="value">{fps_stats['average']:.1f}</span></p>
                            <p>{self.text['peak']}: <span class="value peak">{fps_stats['peak']:.1f}</span></p>
                            <p>{self.text['min']}: <span class="value min">{fps_stats['min']:.1f}</span></p>
                        </div>
                    </div>
                    
                    <div class="charts-panel">
                        <div class="chart-container">
                            <h2>{self.text['overview_chart']}</h2>
                            <img src="performance_overview.png" alt="Performance Chart">
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 保存HTML文件
        with open(os.path.join(report_dir, 'report.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    def calculate_performance_score(self, stats, fps_data):
        # Calculate base score (0-100)
        cpu_score = max(0, 100 - stats['cpu']['stats']['average'])
        memory_score = max(0, 100 - stats['memory']['stats']['average'])
        gpu_score = max(0, 100 - stats['gpu']['stats']['average'])
        
        # Calculate FPS score
        avg_fps = np.mean(fps_data) if fps_data else 0
        fps_score = min(100, (avg_fps / 60.0) * 100)  # Normalize to 60 FPS
        
        # Calculate stability scores (based on standard deviation)
        cpu_stability = max(0, 100 - np.std(stats['cpu']['values']) if stats['cpu']['values'] else 0)
        fps_stability = max(0, 100 - np.std(fps_data) if fps_data else 0)
        
        # Weighted final score
        weights = {
            'cpu': 0.2,
            'memory': 0.15,
            'gpu': 0.2,
            'fps': 0.3,
            'stability': 0.15
        }
        
        final_score = (
            weights['cpu'] * cpu_score +
            weights['memory'] * memory_score +
            weights['gpu'] * gpu_score +
            weights['fps'] * fps_score +
            weights['stability'] * (cpu_stability * 0.5 + fps_stability * 0.5)
        )
        
        return round(final_score, 1)