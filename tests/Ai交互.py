import sounddevice as sd
import numpy as np

# 音量阈值
# 数值越小越敏感
THRESHOLD = 0.02


def callback(indata, frames, time, status):
    """
    麦克风实时回调函数
    indata: 当前录制到的音频数据
    """

    # 计算当前音量大小
    volume = np.linalg.norm(indata)

    # 判断是否有人说话
    if volume > THRESHOLD:
        print("🎤 有人说话")
    else:
        print("🤫 监听中...")


def main():
    """
    主函数
    """

    print("开始监听麦克风...")

    # 打开麦克风输入流
    with sd.InputStream(callback=callback):

        # 每1秒检测一次
        while True:
            sd.sleep(1000)


if __name__ == '__main__':
    main()