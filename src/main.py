import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QComboBox, QCheckBox, QPushButton, 
                            QLabel, QGroupBox, QTextEdit, QSpinBox, QDialog,
                            QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from audio_manager import AudioManager

class SettingsDialog(QDialog):
    def __init__(self, audio_manager, parent=None):
        super().__init__(parent)
        self.audio_manager = audio_manager
        self.setWindowTitle("音频设置")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        
        # 音频带宽设置
        self.audio_bandwidth = QSpinBox()
        self.audio_bandwidth.setRange(1000, 48000)
        self.audio_bandwidth.setValue(self.audio_manager.audio_bandwidth)
        layout.addRow("音频采集带宽 (Hz):", self.audio_bandwidth)
        
        # CW频率设置
        self.cw_frequency = QSpinBox()
        self.cw_frequency.setRange(300, 3000)
        self.cw_frequency.setValue(self.audio_manager.cw_frequency)
        layout.addRow("CW编码频率 (Hz):", self.cw_frequency)
        
        # CW带宽设置
        self.cw_bandwidth = QSpinBox()
        self.cw_bandwidth.setRange(50, 500)
        self.cw_bandwidth.setValue(self.audio_manager.cw_bandwidth)
        layout.addRow("CW模式截取带宽 (Hz):", self.cw_bandwidth)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)

    def get_settings(self):
        return {
            'audio_bandwidth': self.audio_bandwidth.value(),
            'cw_frequency': self.cw_frequency.value(),
            'cw_bandwidth': self.cw_bandwidth.value()
        }

class AutoMorseMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_manager = AudioManager()
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
        
        # 测试音频按钮
        test_layout = QHBoxLayout()
        self.test_tone_btn = QPushButton("测试音频")
        self.test_tone_btn.clicked.connect(self.toggle_test_tone)
        test_layout.addWidget(self.test_tone_btn)
        audio_layout.addLayout(test_layout)
        
        # 音频参数设置按钮
        self.audio_settings_btn = QPushButton("音频参数设置")
        self.audio_settings_btn.clicked.connect(self.show_audio_settings)
        audio_layout.addWidget(self.audio_settings_btn)
        
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
        
        # 初始化音频设备
        self.init_audio_devices()
        
        # 加载配置
        self.load_config()
        
        # 连接信号
        self.connect_signals()
        
    def init_audio_devices(self):
        """初始化音频设备列表"""
        input_devices, output_devices = self.audio_manager.get_audio_devices()
        
        # 清空并添加输入设备
        self.input_device.clear()
        for device in input_devices:
            self.input_device.addItem(device['name'], device['index'])
            
        # 清空并添加输出设备
        self.output_device.clear()
        self.monitor_device.clear()
        for device in output_devices:
            self.output_device.addItem(device['name'], device['index'])
            self.monitor_device.addItem(device['name'], device['index'])
            
    def connect_signals(self):
        """连接信号和槽"""
        self.input_device.currentIndexChanged.connect(self.on_input_device_changed)
        self.output_device.currentIndexChanged.connect(self.on_output_device_changed)
        self.monitor_device.currentIndexChanged.connect(self.on_monitor_device_changed)
        self.monitor_audio.stateChanged.connect(self.on_monitor_audio_changed)
        
    def on_input_device_changed(self, index):
        """输入设备改变时的处理"""
        device_index = self.input_device.currentData()
        self.audio_manager.set_input_device(device_index)
        self.save_config()
        
    def on_output_device_changed(self, index):
        """输出设备改变时的处理"""
        device_index = self.output_device.currentData()
        self.audio_manager.set_output_device(device_index)
        self.save_config()
        
    def on_monitor_device_changed(self, index):
        """监听设备改变时的处理"""
        device_index = self.monitor_device.currentData()
        self.audio_manager.set_monitor_device(device_index)
        self.save_config()
        
    def on_monitor_audio_changed(self, state):
        """监听音频状态改变时的处理"""
        if state == Qt.CheckState.Checked.value:
            # TODO: 实现音频监听功能
            pass
        else:
            # TODO: 停止音频监听
            pass
            
    def toggle_test_tone(self):
        """切换测试音频的播放状态"""
        if self.audio_manager.is_testing:
            self.audio_manager.stop_test_tone()
            self.test_tone_btn.setText("测试音频")
        else:
            self.audio_manager.play_test_tone(self.audio_manager.cw_frequency)
            self.test_tone_btn.setText("停止测试")
            
    def show_audio_settings(self):
        """显示音频参数设置对话框"""
        dialog = SettingsDialog(self.audio_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            self.audio_manager.set_audio_bandwidth(settings['audio_bandwidth'])
            self.audio_manager.set_cw_frequency(settings['cw_frequency'])
            self.audio_manager.set_cw_bandwidth(settings['cw_bandwidth'])
            self.save_config()
        
    def load_config(self):
        """加载配置"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.audio_manager.load_settings(config)
                
                # 设置设备选择
                if config.get('input_device') is not None:
                    index = self.input_device.findData(config['input_device'])
                    if index >= 0:
                        self.input_device.setCurrentIndex(index)
                        
                if config.get('output_device') is not None:
                    index = self.output_device.findData(config['output_device'])
                    if index >= 0:
                        self.output_device.setCurrentIndex(index)
                        
                if config.get('monitor_device') is not None:
                    index = self.monitor_device.findData(config['monitor_device'])
                    if index >= 0:
                        self.monitor_device.setCurrentIndex(index)
                        
                self.monitor_audio.setChecked(config.get('monitor_audio', False))
                self.auto_send_cb.setChecked(config.get('auto_send', False))
                self.local_log_cb.setChecked(config.get('local_log', False))
                self.remote_log_cb.setChecked(config.get('remote_log', False))
                
        except FileNotFoundError:
            # 如果配置文件不存在，创建默认配置
            self.save_config()
    
    def save_config(self):
        """保存配置"""
        config = {
            'input_device': self.audio_manager.input_device,
            'output_device': self.audio_manager.output_device,
            'monitor_device': self.audio_manager.monitor_device,
            'audio_bandwidth': self.audio_manager.audio_bandwidth,
            'cw_frequency': self.audio_manager.cw_frequency,
            'cw_bandwidth': self.audio_manager.cw_bandwidth,
            'monitor_audio': self.monitor_audio.isChecked(),
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