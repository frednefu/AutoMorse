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

    def wpm_to_durations(self, wpm):
        # 国际摩尔斯码标准：1 WPM = 50单位/分钟 = 1.2s/字母 = 60/(50*wpm)秒/单位
        unit = 60 / (50 * wpm)
        dot = unit
        dash = 3 * unit
        space = unit
        word_space = 7 * unit
        return dot, dash, space, word_space

    def morse_to_audio(self, morse, frequency, wpm=26):
        """将摩尔斯码转换为音频信号，支持速度wpm"""
        dot_duration, dash_duration, space_duration, word_space_duration = self.wpm_to_durations(wpm)
        audio = []
        for char in morse:
            if char == '.':
                dot_samples = int(dot_duration * self.sample_rate)
                t = np.linspace(0, dot_duration, dot_samples, False, dtype=np.float32)
                audio.extend(np.sin(2 * np.pi * frequency * t, dtype=np.float32))
                space_samples = int(space_duration * self.sample_rate)
                audio.extend(np.zeros(space_samples, dtype=np.float32))
            elif char == '-':
                dash_samples = int(dash_duration * self.sample_rate)
                t = np.linspace(0, dash_duration, dash_samples, False, dtype=np.float32)
                audio.extend(np.sin(2 * np.pi * frequency * t, dtype=np.float32))
                space_samples = int(space_duration * self.sample_rate)
                audio.extend(np.zeros(space_samples, dtype=np.float32))
            elif char == ' ':
                space_samples = int(word_space_duration * self.sample_rate)
                audio.extend(np.zeros(space_samples, dtype=np.float32))
        return np.array(audio, dtype=np.float32)

    def generate_cq_audio(self, frequency, wpm=26):
        """生成CQ CQ CQ的摩尔斯码音频，支持速度wpm"""
        text = "CQ CQ CQ"
        morse = self.text_to_morse(text)
        return self.morse_to_audio(morse, frequency, wpm) 