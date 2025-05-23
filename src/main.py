import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QComboBox, QCheckBox, QPushButton, 
                            QLabel, QGroupBox, QTextEdit, QSpinBox, QDialog,
                            QFormLayout, QDialogButtonBox, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QTextCursor
import pyqtgraph as pg
import numpy as np
from audio_manager import AudioManager
import PyQt6.QtGui

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
        # 连接测试完成信号
        self.audio_manager.test_completed.connect(self.on_test_completed)
        # 连接发送完成信号
        self.audio_manager.send_completed.connect(self.on_send_completed)
        # 连接发送单个字符完成信号
        self.audio_manager.character_sent.connect(self.on_character_sent)
        self.setWindowTitle("AutoMorse - CW自动收发系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建用于自动发送的定时器
        self.auto_send_timer = QTimer(self)
        self.auto_send_timer.setInterval(300) # 设置延迟为300ms
        self.auto_send_timer.setSingleShot(True) # 只触发一次
        self.auto_send_timer.timeout.connect(self.trigger_auto_send)
        
        # 自动发送模式标志
        self.is_auto_sending_active = False
        
        # 已发送的文本（用于自动发送时比较）
        self.sent_text_content = ""
        
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
        
        # 常规设置组（移到最顶部，独立分组）
        general_group = QGroupBox("常规设置")
        general_layout = QFormLayout()
        self.callsign_edit = QLineEdit()
        self.callsign_edit.setPlaceholderText("请输入呼号")
        general_layout.addRow(QLabel("呼号："), self.callsign_edit)
        self.grid_edit = QLineEdit()
        self.grid_edit.setPlaceholderText("请输入网格")
        general_layout.addRow(QLabel("网格："), self.grid_edit)
        general_group.setLayout(general_layout)
        left_layout.addWidget(general_group)
        
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
        receive_label_layout = QHBoxLayout()
        receive_label_layout.addWidget(QLabel("接收CW信息："))
        self.receive_speed_spin = QSpinBox()
        self.receive_speed_spin.setRange(5, 60)
        self.receive_speed_spin.setValue(26)
        self.receive_speed_spin.setSuffix(" WPM")
        self.receive_speed_spin.setFixedWidth(100)
        self.receive_speed_spin.setToolTip("接收CW报文速度")
        self.receive_speed_spin.setEnabled(True)
        self.receive_speed_auto_cb = QCheckBox("自动模式")
        self.receive_speed_auto_cb.setChecked(True)
        self.receive_speed_auto_cb.setToolTip("自动检测接收速度")
        receive_label_layout.addWidget(self.receive_speed_spin)
        receive_label_layout.addWidget(self.receive_speed_auto_cb)
        receive_label_layout.addStretch()
        receive_layout.addLayout(receive_label_layout)
        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)
        receive_layout.addWidget(self.receive_text)
        cw_layout.addLayout(receive_layout)
        
        # 发送信息 (待发送信息文本框)
        send_layout = QVBoxLayout()
        send_label_layout = QHBoxLayout()
        send_label_layout.addWidget(QLabel("发送CW信息：")) # 这里的标签依然是"发送CW信息："
        self.send_speed_spin = QSpinBox()
        self.send_speed_spin.setRange(5, 60)
        self.send_speed_spin.setValue(26)
        self.send_speed_spin.setSuffix(" WPM")
        self.send_speed_spin.setFixedWidth(100)
        self.send_speed_spin.setToolTip("发送CW报文速度")
        send_label_layout.addWidget(self.send_speed_spin)
        send_label_layout.addStretch()
        send_layout.addLayout(send_label_layout)
        self.send_text = QTextEdit() # 这是待发送信息文本框
        # 连接 textChanged 信号
        self.send_text.textChanged.connect(self.on_send_text_changed)
        send_layout.addWidget(self.send_text)
        # 将发送信息布局添加到主CW布局
        cw_layout.addLayout(send_layout)
        
        # 已发信息显示区域
        sent_layout = QVBoxLayout()
        sent_label = QLabel("已发信息：")
        sent_layout.addWidget(sent_label)
        self.sent_text = QTextEdit()
        self.sent_text.setReadOnly(True) # 设置为只读
        self.sent_text.setStyleSheet("color: red;") # 设置文字颜色为红色
        self.sent_text.setFixedHeight(4 * self.sent_text.fontMetrics().lineSpacing()) # 设置显示高度为4行
        sent_layout.addWidget(self.sent_text)
        # 将已发信息布局添加到主CW布局
        cw_layout.addLayout(sent_layout)
        
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
        self.receive_speed_auto_cb.stateChanged.connect(self.on_receive_speed_auto_changed)
        self.send_btn.clicked.connect(self.on_send_btn_clicked)
        self.callsign_edit.textChanged.connect(self.save_config)
        self.grid_edit.textChanged.connect(self.save_config)
        self.test_tone_btn.clicked.connect(self.toggle_test_tone)
        
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
        print(f"toggle_test_tone: is_testing = {self.audio_manager.is_testing}")  # 调试信息
        if not self.audio_manager.is_testing:
            # 开始测试
            wpm = self.send_speed_spin.value() # 测试音频使用发送速度
            freq = self.audio_manager.cw_frequency
            print(f"开始测试音频: freq={freq}, wpm={wpm}")  # 调试信息
            # 先更新按钮状态，再开始播放
            self.update_test_button_state(True)
            # 使用QTimer延迟调用play_test_tone，避免按钮状态更新和音频播放的竞争
            QTimer.singleShot(50, lambda: self.audio_manager.play_test_tone(freq, wpm))
        else:
            # 停止测试
            print("停止测试音频")  # 调试信息
            # 先更新按钮状态，再停止播放
            self.update_test_button_state(False)
            # 使用QTimer延迟调用stop_test_tone，确保按钮状态已更新
            QTimer.singleShot(50, self.audio_manager.stop_test_tone)

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
                # 加载速度设置
                self.receive_speed_spin.setValue(config.get('receive_cw_speed', 26))
                self.receive_speed_auto_cb.setChecked(config.get('receive_cw_speed_auto', True))
                self.send_speed_spin.setValue(config.get('send_cw_speed', 26))
                # 加载常规设置
                self.callsign_edit.setText(config.get('callsign', ''))
                self.grid_edit.setText(config.get('grid', ''))
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
            'remote_log': self.remote_log_cb.isChecked(),
            # 新增速度设置
            'receive_cw_speed': self.receive_speed_spin.value(),
            'receive_cw_speed_auto': self.receive_speed_auto_cb.isChecked(),
            'send_cw_speed': self.send_speed_spin.value(),
            # 常规设置
            'callsign': self.callsign_edit.text(),
            'grid': self.grid_edit.text()
        }
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    def on_receive_speed_auto_changed(self, state):
        if state == Qt.CheckState.Checked.value:
            self.receive_speed_spin.setEnabled(False)
        else:
            self.receive_speed_spin.setEnabled(True)
        self.save_config()

    def on_send_btn_clicked(self):
        """点击发送按钮，根据状态切换发送/停止"""
        print(f"on_send_btn_clicked: is_sending = {self.audio_manager.is_sending}, is_auto_sending_active = {self.is_auto_sending_active}") # 调试信息
        
        if not self.audio_manager.is_sending and not self.is_auto_sending_active:
            # 如果当前不在发送状态且不在自动发送模式，则开始新的发送并进入自动发送模式
            print("开始手动发送并进入自动发送模式") # 调试信息
            self.is_auto_sending_active = True
            self.update_send_button_state(True)
            # 清空已发信息文本框
            self.sent_text.clear()
            self.sent_text_content = "" # 清空已发送文本记录
            text = self.send_text.toPlainText()
            wpm = self.send_speed_spin.value()
            freq = self.audio_manager.cw_frequency
            # 直接调用send_cw，它会按字符发送并发出信号
            self.audio_manager.send_cw(text, freq, wpm)
            
        elif self.audio_manager.is_sending or self.is_auto_sending_active:
             # 如果当前正在发送或在自动发送模式，则停止发送并退出自动发送模式
             print("停止发送并退出自动发送模式") # 调试信息
             self.is_auto_sending_active = False
             self.auto_send_timer.stop() # 停止自动发送定时器
             self.audio_manager.stop_sending_cw()
             self.update_send_button_state(False) # 立即更新按钮状态为发送

    def update_send_button_state(self, is_sending):
        """更新发送按钮的状态和颜色"""
        print(f"update_send_button_state: is_sending = {is_sending}") # 调试信息
        if is_sending:
            self.send_btn.setText("停止发送")
            # 设置按钮样式，包括hover状态
            self.send_btn.setStyleSheet("""
                QPushButton#send_btn {
                    background-color: red !important;
                    color: white !important;
                }
                QPushButton#send_btn:hover {
                    background-color: red !important;
                }
            """)
            self.send_btn.setEnabled(True) # 确保按钮是启用的
            print("按钮已更新为停止发送状态") # 调试信息
        else:
            self.send_btn.setText("发送")
            self.send_btn.setStyleSheet("") # 恢复默认样式
            self.send_btn.setEnabled(True) # 确保按钮是启用的
            print("按钮已更新为发送状态") # 调试信息

        # 同时检查测试音频按钮的状态，避免两个按钮都是红色
        if not is_sending and not self.audio_manager.is_testing:
            self.test_tone_btn.setStyleSheet("")
            self.test_tone_btn.setEnabled(True) # 确保测试按钮也是启用的

    def update_test_button_state(self, is_testing):
        """更新测试音频按钮的状态和颜色"""
        print(f"update_test_button_state: is_testing = {is_testing}")  # 调试信息
        if is_testing:
            self.test_tone_btn.setText("停止测试")
            # 设置按钮样式，包括hover状态，使用更具体的选择器和!important
            self.test_tone_btn.setStyleSheet("""
                QPushButton#test_tone_btn {
                    background-color: red !important;
                    color: white !important;
                }
                QPushButton#test_tone_btn:hover {
                    background-color: red !important;
                }
            """)
            self.test_tone_btn.setEnabled(True) # 确保按钮是启用的
            print("按钮已更新为停止测试状态")  # 调试信息
        else:
            self.test_tone_btn.setText("测试音频")
            self.test_tone_btn.setStyleSheet("") # 恢复默认样式
            self.test_tone_btn.setEnabled(True) # 确保按钮是启用的
            print("按钮已更新为测试音频状态")  # 调试信息
        # 同时检查发送按钮的状态，避免两个按钮都是红色
        if not is_testing and not self.audio_manager.is_sending:
            self.send_btn.setStyleSheet("")
            self.send_btn.setEnabled(True) # 确保发送按钮也是启用的

    def on_send_completed(self):
        """发送音频播放完成的处理函数"""
        print("收到发送完成信号")  # 调试信息
        print(f"on_send_completed: before check is_auto_sending_active={self.is_auto_sending_active}") # 新增调试信息
        # 发送完成后，如果自动发送模式仍然开启，则等待新的文本输入触发自动发送
        if self.is_auto_sending_active:
            print("发送完成，自动发送模式开启，等待新的文本") # 调试信息
        else:
            # 如果自动发送模式已关闭（用户点击了停止按钮），则不做额外操作，按钮状态已更新
            print("发送完成，自动发送模式已关闭") # 调试信息
        print(f"on_send_completed: after check is_auto_sending_active={self.is_auto_sending_active}") # 新增调试信息

    def on_test_completed(self):
        """测试音频播放完成的处理函数"""
        print("收到测试完成信号")  # 调试信息
        self.update_test_button_state(False)

    def on_send_text_changed(self):
        """发送文本框内容改变时的处理"""
        print("on_send_text_changed triggered") # 调试信息
        try:
            print("Getting cursor") # 调试信息
            cursor = self.send_text.textCursor()
            print("Moving cursor to end") # 调试信息
            cursor.movePosition(PyQt6.QtGui.QTextCursor.MoveMode.End)
            self.send_text.setTextCursor(cursor) # 立即设置光标位置
            print("Getting plain text") # 调试信息
            text = self.send_text.toPlainText()
            print(f"Original text: {text}") # 调试信息
            
            print("Starting filtering loop") # 调试信息
            filtered_chars = []
            for c in text:
                if c.isalnum() or c.isspace():
                    filtered_chars.append(c.upper())
            filtered_text = "".join(filtered_chars)
            print("Filtering loop finished") # 调试信息
            print(f"Filtered text: {filtered_text}") # 调试信息
            
            if filtered_text != text:
                print("Text needs update") # 调试信息
                self.send_text.blockSignals(True) # 阻止信号，避免无限循环
                self.send_text.setText(filtered_text)
                # 恢复光标位置
                new_cursor = self.send_text.textCursor()
                new_cursor.movePosition(PyQt6.QtGui.QTextCursor.MoveMode.End)
                self.send_text.setTextCursor(new_cursor)
                self.send_text.blockSignals(False)
            else:
                print("Text is already correct") # 调试信息
            
            # 如果自动发送模式开启且有新内容需要发送，则启动延迟发送
            # 判断新内容：当前文本框内容长度 > 已发送文本记录长度
            if self.is_auto_sending_active and len(filtered_text) > len(self.sent_text_content):
                 print("文本改变，自动发送模式开启，有新内容，启动定时器") # 调试信息
                 self.auto_send_timer.start() # 启动或重置定时器
            elif not filtered_text.strip():
                # 如果文本清空，停止定时器并退出自动发送模式（如果开启）
                if self.is_auto_sending_active:
                     print("文本清空，退出自动发送模式") # 调试信息
                     self.is_auto_sending_active = False
                     self.auto_send_timer.stop()
                     if self.send_btn.text() == "停止发送":
                          self.update_send_button_state(False)
        except Exception as e:
            print(f"Error in on_send_text_changed: {e}") # 捕获并打印异常

    def trigger_auto_send(self):
        """触发自动发送，发送新增的字符"""
        print("触发自动发送") # 调试信息
        # 只有在自动发送模式开启且当前没有发送时才进行自动发送
        if self.is_auto_sending_active and not self.audio_manager.is_sending:
             print("执行自动发送，查找新内容") # 调试信息
             current_text = self.send_text.toPlainText()
             # 找到需要发送的新字符
             new_chars = current_text[len(self.sent_text_content):]

             if new_chars:
                  print(f"发送新字符: {new_chars}") # 调试信息
                  wpm = self.send_speed_spin.value()
                  freq = self.audio_manager.cw_frequency
                  # 调用 send_cw 发送新字符，send_cw现在会处理按字符发送和信号
                  self.audio_manager.send_cw(new_chars, freq, wpm)
                  # send_cw 发送完毕后会发出 character_sent 信号，在on_character_sent中更新sent_text_content
             else:
                  print("没有新字符需要发送") # 调试信息
        else:
             print(f"不执行自动发送：is_auto_sending_active={self.is_auto_sending_active}, is_sending={self.audio_manager.is_sending}") # 调试信息

    def on_character_sent(self, char):
        """接收到单个字符发送完成信号，更新已发信息文本框"""
        print(f"收到字符发送完成信号: {char}") # 调试信息
        self.sent_text.append(char) # 在已发信息文本框中添加字符
        self.sent_text_content += char # 更新已发送文本记录

def main():
    app = QApplication(sys.argv)
    window = AutoMorseMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 