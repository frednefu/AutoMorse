import numpy as np

class MorseUtils:
    # 摩尔斯码定义
    MORSE_CODE = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
        '9': '----.', '0': '-----', ' ': ' '
    }

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # 摩尔斯码时间单位（秒）
        self.dot_duration = 0.1  # 点的时间
        self.dash_duration = 0.3  # 划的时间
        self.space_duration = 0.1  # 字符内间隔
        self.word_space_duration = 0.3  # 词间隔

    def text_to_morse(self, text):
        """将文本转换为摩尔斯码"""
        morse = []
        for char in text.upper():
            if char in self.MORSE_CODE:
                morse.append(self.MORSE_CODE[char])
            else:
                morse.append(' ')
        return ' '.join(morse)

    def morse_to_audio(self, morse, frequency):
        """将摩尔斯码转换为音频信号"""
        audio = []
        for char in morse:
            if char == '.':
                # 生成点的音频
                dot_samples = int(self.dot_duration * self.sample_rate)
                t = np.linspace(0, self.dot_duration, dot_samples, False, dtype=np.float32)
                audio.extend(np.sin(2 * np.pi * frequency * t, dtype=np.float32))
                # 添加字符内间隔
                space_samples = int(self.space_duration * self.sample_rate)
                audio.extend(np.zeros(space_samples, dtype=np.float32))
            elif char == '-':
                # 生成划的音频
                dash_samples = int(self.dash_duration * self.sample_rate)
                t = np.linspace(0, self.dash_duration, dash_samples, False, dtype=np.float32)
                audio.extend(np.sin(2 * np.pi * frequency * t, dtype=np.float32))
                # 添加字符内间隔
                space_samples = int(self.space_duration * self.sample_rate)
                audio.extend(np.zeros(space_samples, dtype=np.float32))
            elif char == ' ':
                # 添加词间隔
                space_samples = int(self.word_space_duration * self.sample_rate)
                audio.extend(np.zeros(space_samples, dtype=np.float32))

        return np.array(audio, dtype=np.float32)

    def generate_cq_audio(self, frequency):
        """生成CQ CQ CQ的摩尔斯码音频"""
        text = "CQ CQ CQ"
        morse = self.text_to_morse(text)
        return self.morse_to_audio(morse, frequency) 