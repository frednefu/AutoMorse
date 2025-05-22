import sounddevice as sd
import numpy as np
import threading
import time
from morse_utils import MorseUtils

class AudioManager:
    def __init__(self):
        self.input_device = None
        self.output_device = None
        self.monitor_device = None
        self.sample_rate = 44100
        self.audio_bandwidth = 3000  # 默认音频采集带宽
        self.cw_frequency = 700      # 默认CW编码频率
        self.cw_bandwidth = 150      # 默认CW模式截取带宽
        self.is_testing = False
        self.test_thread = None
        self.morse_utils = MorseUtils(self.sample_rate)
        self.stream = None
        self._lock = threading.Lock()

    def get_audio_devices(self):
        """获取所有音频设备"""
        devices = sd.query_devices()
        input_devices = []
        output_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels']
                })
            if device['max_output_channels'] > 0:
                output_devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_output_channels']
                })
        
        return input_devices, output_devices

    def set_input_device(self, device_index):
        """设置输入设备"""
        self.input_device = device_index

    def set_output_device(self, device_index):
        """设置输出设备"""
        self.output_device = device_index

    def set_monitor_device(self, device_index):
        """设置监听设备"""
        self.monitor_device = device_index

    def set_audio_bandwidth(self, bandwidth):
        """设置音频采集带宽"""
        self.audio_bandwidth = bandwidth

    def set_cw_frequency(self, frequency):
        """设置CW编码频率"""
        self.cw_frequency = frequency

    def set_cw_bandwidth(self, bandwidth):
        """设置CW模式截取带宽"""
        self.cw_bandwidth = bandwidth

    def generate_test_tone(self, frequency, duration=1.0):
        """生成测试音频"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t)
        return tone

    def play_test_tone(self, frequency):
        """播放测试音频"""
        with self._lock:
            if self.is_testing:
                self.stop_test_tone()
                return
            
            self.is_testing = True
            self.test_thread = threading.Thread(target=self._test_tone_loop, args=(frequency,))
            self.test_thread.start()

    def stop_test_tone(self):
        """停止测试音频"""
        with self._lock:
            if not self.is_testing:
                return
                
            self.is_testing = False
            
            if self.stream is not None:
                try:
                    self.stream.abort()
                except:
                    pass
                try:
                    self.stream.close()
                except:
                    pass
                self.stream = None
                
            if self.test_thread:
                self.test_thread.join(timeout=1.0)
                self.test_thread = None

    def _test_tone_loop(self, frequency):
        """测试音频循环播放"""
        try:
            # 创建音频流
            with self._lock:
                if not self.is_testing:
                    return
                    
                self.stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    device=self.monitor_device,
                    dtype=np.float32,
                    blocksize=1024
                )
                self.stream.start()

            while self.is_testing:
                # 生成CQ CQ CQ的摩尔斯码音频
                audio = self.morse_utils.generate_cq_audio(frequency)
                
                # 确保音频数据是二维的 (samples, channels)
                if audio.ndim == 1:
                    audio = audio.reshape(-1, 1)
                
                # 播放音频
                with self._lock:
                    if self.stream is not None and self.is_testing:
                        try:
                            self.stream.write(audio)
                        except:
                            break
                
                # 如果已经停止，退出循环
                if not self.is_testing:
                    break
                    
                # 添加一个短暂的停顿
                time.sleep(1.0)

        except Exception as e:
            print(f"音频播放错误: {e}")
        finally:
            with self._lock:
                self.is_testing = False
                if self.stream is not None:
                    try:
                        self.stream.abort()
                    except:
                        pass
                    try:
                        self.stream.close()
                    except:
                        pass
                    self.stream = None

    def get_current_settings(self):
        """获取当前设置"""
        return {
            'input_device': self.input_device,
            'output_device': self.output_device,
            'monitor_device': self.monitor_device,
            'audio_bandwidth': self.audio_bandwidth,
            'cw_frequency': self.cw_frequency,
            'cw_bandwidth': self.cw_bandwidth
        }

    def load_settings(self, settings):
        """加载设置"""
        self.input_device = settings.get('input_device')
        self.output_device = settings.get('output_device')
        self.monitor_device = settings.get('monitor_device')
        self.audio_bandwidth = settings.get('audio_bandwidth', 3000)
        self.cw_frequency = settings.get('cw_frequency', 700)
        self.cw_bandwidth = settings.get('cw_bandwidth', 150) 