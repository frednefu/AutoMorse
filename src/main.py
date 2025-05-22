import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QComboBox, QCheckBox, QPushButton, 
                            QLabel, QGroupBox, QTextEdit)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np

class AutoMorseMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoMorse - CW自动收发系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建主布局
        layout = QHBoxLayout()
        main_widget.setLayout(layout)
        
        # 左侧控制面板
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # 音频设置组
        audio_group = QGroupBox("音频设置")
        audio_layout = QVBoxLayout()
        
        # 输入设备
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("输入设备："))
        self.input_device = QComboBox()
        input_layout.addWidget(self.input_device)
        audio_layout.addLayout(input_layout)
        
        # 输出设备
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出设备："))
        self.output_device = QComboBox()
        output_layout.addWidget(self.output_device)
        audio_layout.addLayout(output_layout)
        
        # 监听设备
        monitor_layout = QHBoxLayout()
        monitor_layout.addWidget(QLabel("监听设备："))
        self.monitor_device = QComboBox()
        monitor_layout.addWidget(self.monitor_device)
        audio_layout.addLayout(monitor_layout)
        
        # 监听音频复选框
        self.monitor_audio = QCheckBox("监听音频")
        audio_layout.addWidget(self.monitor_audio)
        
        audio_group.setLayout(audio_layout)
        left_layout.addWidget(audio_group)
        
        # 大语言模型设置组
        model_group = QGroupBox("大语言模型设置")
        model_layout = QVBoxLayout()
        
        model_select_layout = QHBoxLayout()
        model_select_layout.addWidget(QLabel("模型："))
        self.model_select = QComboBox()
        model_select_layout.addWidget(self.model_select)
        model_layout.addLayout(model_select_layout)
        
        install_model_btn = QPushButton("安装模型")
        model_layout.addWidget(install_model_btn)
        
        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)
        
        # 添加左侧面板到主布局
        layout.addWidget(left_panel, stretch=1)
        
        # 右侧显示面板
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # 频谱图
        spectrum_group = QGroupBox("频谱图")
        spectrum_layout = QVBoxLayout()
        self.spectrum_plot = pg.PlotWidget()
        spectrum_layout.addWidget(self.spectrum_plot)
        spectrum_group.setLayout(spectrum_layout)
        right_layout.addWidget(spectrum_group)
        
        # 瀑布图
        waterfall_group = QGroupBox("瀑布图")
        waterfall_layout = QVBoxLayout()
        self.waterfall_plot = pg.PlotWidget()
        waterfall_layout.addWidget(self.waterfall_plot)
        waterfall_group.setLayout(waterfall_layout)
        right_layout.addWidget(waterfall_group)
        
        # CW信息显示区域
        cw_group = QGroupBox("CW信息")
        cw_layout = QVBoxLayout()
        
        # 接收信息
        receive_layout = QVBoxLayout()
        receive_layout.addWidget(QLabel("接收CW信息："))
        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)
        receive_layout.addWidget(self.receive_text)
        cw_layout.addLayout(receive_layout)
        
        # 发送信息
        send_layout = QVBoxLayout()
        send_layout.addWidget(QLabel("发送CW信息："))
        self.send_text = QTextEdit()
        send_layout.addWidget(self.send_text)
        cw_layout.addLayout(send_layout)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        self.start_receive_btn = QPushButton("开始接收")
        self.send_btn = QPushButton("发送")
        self.auto_send_cb = QCheckBox("自动发送")
        self.local_log_cb = QCheckBox("本地日志")
        self.remote_log_cb = QCheckBox("远程日志")
        self.settings_btn = QPushButton("设置")
        
        control_layout.addWidget(self.start_receive_btn)
        control_layout.addWidget(self.send_btn)
        control_layout.addWidget(self.auto_send_cb)
        control_layout.addWidget(self.local_log_cb)
        control_layout.addWidget(self.remote_log_cb)
        control_layout.addWidget(self.settings_btn)
        
        cw_layout.addLayout(control_layout)
        cw_group.setLayout(cw_layout)
        right_layout.addWidget(cw_group)
        
        # 添加右侧面板到主布局
        layout.addWidget(right_panel, stretch=2)
        
        # 加载配置
        self.load_config()
        
    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                # TODO: 加载配置到界面
        except FileNotFoundError:
            # 如果配置文件不存在，创建默认配置
            self.save_config()
    
    def save_config(self):
        config = {
            'input_device': self.input_device.currentText(),
            'output_device': self.output_device.currentText(),
            'monitor_device': self.monitor_device.currentText(),
            'monitor_audio': self.monitor_audio.isChecked(),
            'model': self.model_select.currentText(),
            'auto_send': self.auto_send_cb.isChecked(),
            'local_log': self.local_log_cb.isChecked(),
            'remote_log': self.remote_log_cb.isChecked()
        }
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

def main():
    app = QApplication(sys.argv)
    window = AutoMorseMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 