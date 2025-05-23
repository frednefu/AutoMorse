import sounddevice as sd
import numpy as np
import threading
import time
from morse_utils import MorseUtils
from PyQt6.QtCore import QObject, pyqtSignal

class AudioManager(QObject):
    # 定义信号
    test_completed = pyqtSignal()  # 测试音频播放完成信号
    
    def __init__(self):
        super().__init__()  # 调用父类初始化
        self.input_device = None
        self.output_device = None
        self.monitor_device = None
        self.sample_rate = 44100
        self.audio_bandwidth = 3000  # 默认音频采集带宽
        self.cw_frequency = 700      # 默认CW编码频率
        self.cw_bandwidth = 150      # 默认CW模式截取带宽
        self.is_testing = False      # 测试音频状态
        self.test_thread = None      # 测试音频线程
        self.test_stream = None      # 测试音频流
        self.is_sending = False      # 发送状态
        self.send_thread = None      # 发送线程
        self.send_stream = None      # 发送音频流
        self.morse_utils = MorseUtils(self.sample_rate)
        self._lock = threading.Lock()
        self.send_cw_speed = 26      # 默认发送速度WPM

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

    def set_send_cw_speed(self, wpm):
        self.send_cw_speed = wpm

    def get_send_cw_speed(self):
        return self.send_cw_speed

    def generate_test_tone(self, frequency, duration=1.0):
        """生成测试音频"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t)
        return tone

    def play_test_tone(self, frequency, wpm=26):
        """播放测试音频，支持速度wpm"""
        print(f"play_test_tone: frequency={frequency}, wpm={wpm}")  # 调试信息
        with self._lock:
            # 如果正在测试或发送，则不开始新的测试
            if self.is_testing or self.is_sending:
                print("已经在测试或发送中，不开始新的测试")  # 调试信息
                return
            print("开始新的测试")  # 调试信息
            self.is_testing = True
            self.test_thread = threading.Thread(target=self._test_tone_loop, args=(frequency, wpm))
            self.test_thread.start()

    def stop_test_tone(self):
        """停止测试音频"""
        print("stop_test_tone 被调用")  # 调试信息
        with self._lock:
            if not self.is_testing:
                print("当前没有在测试中")  # 调试信息
                return
            print("停止测试音频")  # 调试信息
            self.is_testing = False
            # 中断测试音频流
            if self.test_stream is not None:
                try:
                    print("尝试中止测试音频流")  # 调试信息
                    self.test_stream.abort()  # 先尝试中止
                    print("尝试停止测试音频流")  # 调试信息
                    self.test_stream.stop()   # 再尝试停止
                    print("尝试关闭测试音频流")  # 调试信息
                    self.test_stream.close()  # 最后关闭
                except Exception as e:
                    print(f"停止测试音频流时出错: {e}")  # 调试信息
                finally:
                    self.test_stream = None
            if self.test_thread:
                print("等待测试线程结束")  # 调试信息
                # 使用较短的超时，避免GUI卡死
                self.test_thread.join(timeout=0.1)
                self.test_thread = None

    def _test_tone_loop(self, frequency, wpm):
        """测试音频播放一次"""
        print(f"_test_tone_loop: frequency={frequency}, wpm={wpm}")  # 调试信息
        try:
            # 生成CQ CQ CQ的摩尔斯码音频 (生成完整的音频)
            audio = self.morse_utils.generate_cq_audio(frequency, wpm)
            audio_len = len(audio)
            print(f"生成了音频数据，长度: {audio_len}")  # 调试信息

            # 创建音频流
            print(f"创建测试音频流，使用设备: {self.monitor_device}")  # 调试信息
            stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                device=self.monitor_device,
                dtype=np.float32,
                blocksize=1024
            )
            
            with self._lock:
                if not self.is_testing:
                    print("测试已被停止，不播放音频")  # 调试信息
                    return
                self.test_stream = stream
                self.test_stream.start()
                print("测试音频流已启动")  # 调试信息

            # 分块播放音频，以便及时响应停止信号
            chunk_size = 1024 # 每次写入的音频帧数
            for i in range(0, audio_len, chunk_size):
                with self._lock:
                    if not self.is_testing: # 在写入前检查停止信号
                        print("检测到停止信号，中断播放")  # 调试信息
                        break
                    chunk = audio[i:i + chunk_size]
                    # 确保chunk是二维的 (samples, channels)
                    if chunk.ndim == 1:
                        chunk = chunk.reshape(-1, 1)

                    if self.test_stream is not None and self.test_stream.active:
                        try:
                            # 使用write方法播放音频块
                            self.test_stream.write(chunk)
                        except Exception as e:
                            print(f"测试音频写入流失败: {e}")
                            break # 写入失败，中断播放
                    else:
                        print("测试音频流非活动或不存在，中断播放")  # 调试信息
                        break

                # 在每次写入后检查停止信号
                if not self.is_testing:
                    print("检测到停止信号，中断播放")  # 调试信息
                    break

        except Exception as e:
            print(f"测试音频播放循环错误: {e}")
        finally:
            with self._lock:
                # 确保is_testing状态最终被设置为False
                if self.is_testing:
                     print("设置is_testing为False")  # 调试信息
                     self.is_testing = False
                if self.test_stream is not None:
                    try:
                        print("尝试停止测试音频流")  # 调试信息
                        self.test_stream.stop()
                        print("尝试关闭测试音频流")  # 调试信息
                        self.test_stream.close()
                    except Exception as e:
                        print(f"关闭测试音频流失败: {e}")  # 调试信息
                    finally:
                        self.test_stream = None
                # 发出测试完成信号
                print("发出测试完成信号")  # 调试信息
                self.test_completed.emit()

    def send_cw(self, text, frequency, wpm):
        """发送CW报文"""
        with self._lock:
            # 如果正在发送或测试，则不开始新的发送
            if self.is_sending or self.is_testing:
                return
            self.is_sending = True
            self.send_thread = threading.Thread(target=self._send_loop, args=(text, frequency, wpm))
            self.send_thread.start()

    def stop_sending_cw(self):
        """停止发送CW报文"""
        with self._lock:
            if not self.is_sending:
                return
            self.is_sending = False
            if self.send_stream is not None:
                try:
                    print("尝试中止发送音频流")  # 调试信息
                    self.send_stream.abort()  # 先尝试中止
                    print("尝试停止发送音频流")  # 调试信息
                    self.send_stream.stop()   # 再尝试停止
                    print("尝试关闭发送音频流")  # 调试信息
                    self.send_stream.close()  # 最后关闭
                except Exception as e:
                    print(f"停止发送音频流时出错: {e}")  # 调试信息
                finally:
                    self.send_stream = None
            if self.send_thread:
                print("等待发送线程结束")  # 调试信息
                # 使用较短的超时，避免GUI卡死
                self.send_thread.join(timeout=0.1)
                self.send_thread = None

    def _send_loop(self, text, frequency, wpm):
        """发送CW报文循环"""
        try:
            morse = self.morse_utils.text_to_morse(text)
            audio = self.morse_utils.morse_to_audio(morse, frequency, wpm)

            with self._lock:
                if not self.is_sending:
                    return
                # 使用 output_device 播放CW报文
                self.send_stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    device=self.output_device,
                    dtype=np.float32,
                    blocksize=1024
                )
                self.send_stream.start()

            # 分块播放音频，以便及时响应停止信号
            chunk_size = 1024 # 每次写入的音频帧数
            for i in range(0, len(audio), chunk_size):
                with self._lock:
                    if not self.is_sending: # 检查停止信号
                        print("发送CW：检测到停止信号，中断播放")  # 调试信息
                        break
                    chunk = audio[i:i + chunk_size]
                    # 确保音频数据是二维的 (samples, channels)
                    if chunk.ndim == 1:
                        chunk = chunk.reshape(-1, 1)

                    if self.send_stream is not None and self.send_stream.active:
                        try:
                            # 使用write方法，如果stream停止会抛异常
                            self.send_stream.write(chunk)
                        except Exception as e:
                            print(f"发送CW写入流失败: {e}")
                            break # 写入失败或停止信号
                    else:
                        print("发送CW：音频流非活动或不存在，中断播放")  # 调试信息
                        break

                # 在每次写入后检查停止信号
                if not self.is_sending:
                    print("发送CW：检测到停止信号，中断播放")  # 调试信息
                    break

        except Exception as e:
            print(f"发送CW音频播放循环错误: {e}")
        finally:
            with self._lock:
                self.is_sending = False
                if self.send_stream is not None:
                    try:
                        print("尝试停止发送音频流")  # 调试信息
                        self.send_stream.stop()
                        print("尝试关闭发送音频流")  # 调试信息
                        self.send_stream.close()
                    except Exception as e:
                        print(f"关闭发送音频流失败: {e}")  # 调试信息
                    finally:
                        self.send_stream = None

    def get_current_settings(self):
        """获取当前设置"""
        return {
            'input_device': self.input_device,
            'output_device': self.output_device,
            'monitor_device': self.monitor_device,
            'audio_bandwidth': self.audio_bandwidth,
            'cw_frequency': self.cw_frequency,
            'cw_bandwidth': self.cw_bandwidth,
            'send_cw_speed': self.send_cw_speed
        }

    def load_settings(self, settings):
        """加载设置"""
        self.input_device = settings.get('input_device')
        self.output_device = settings.get('output_device')
        self.monitor_device = settings.get('monitor_device')
        self.audio_bandwidth = settings.get('audio_bandwidth', 3000)
        self.cw_frequency = settings.get('cw_frequency', 700)
        self.cw_bandwidth = settings.get('cw_bandwidth', 150)
        self.send_cw_speed = settings.get('send_cw_speed', 26) 