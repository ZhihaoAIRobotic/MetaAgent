import pyaudio  
import numpy as np  


def list_audio_devices(pyaudio_instance):  
    """  
    list all the devices
    """  
    print("Available Audio Devices:\n")  
    device_count = pyaudio_instance.get_device_count()  
    for i in range(device_count):  
        device_info = pyaudio_instance.get_device_info_by_index(i)  
        print(f"Device Index: {i}")  
        print(f"  Name: {device_info['name']}")  
        print(f"  Default Sample Rate: {device_info['defaultSampleRate']} Hz")  
        print(f"  Max Input Channels: {device_info['maxInputChannels']}")  
        print(f"  Max Output Channels: {device_info['maxOutputChannels']}")  
        print(f"  Host API: {pyaudio_instance.get_host_api_info_by_index(device_info['hostApi'])['name']}")  
        print("\n")  


def get_supported_sample_rates(pyaudio_instance, device_index, output_format=pyaudio.paInt16, max_channels=2):  
    """  
    detect the supported sample rates for a given device  
    """  
    standard_rates = [8000, 9600, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]  
    supported_rates = []  

    device_info = pyaudio_instance.get_device_info_by_index(device_index)  
    max_channels = device_info.get('maxOutputChannels', max_channels)  

    print(f"Testing supported sample rates for device: {device_info['name']}\n")  
    for rate in standard_rates:  
        try:  
            if pyaudio_instance.is_format_supported(  
                rate,  
                output_device=device_index,  
                output_channels=max_channels,  
                output_format=output_format,  
            ):  
                supported_rates.append(rate)  
                print(f"  Supported: {rate} Hz")  
        except Exception as e:  
            print(f"  Not Supported: {rate} Hz - {e}")  
    return supported_rates  


def generate_sine_wave(frequency, duration, sample_rate, amplitude=0.5):  
    """  
    generate a sine wave for testing audio playback
    """  
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  
    wave = amplitude * np.sin(2 * np.pi * frequency * t)  
    return wave.astype(np.float32)  


def play_audio_stream(pyaudio_instance, device_index, sample_rate, duration=5):  
    """  
    play a sine wave on the selected audio device  
    """  
    try:  
        # 打开音频流  
        stream = pyaudio_instance.open(  
            format=pyaudio.paFloat32,  
            channels=1,  # 单声道  
            rate=sample_rate,  
            output=True,  
            output_device_index=device_index,  
        )  

        print(f"Playing a sine wave at {sample_rate} Hz for {duration} seconds...")  
        # 生成正弦波  
        sine_wave = generate_sine_wave(frequency=440, duration=duration, sample_rate=sample_rate)  

        # 播放音频  
        stream.write(sine_wave.tobytes())  

        # 停止并关闭流  
        stream.stop_stream()  
        stream.close()  
        print("Audio playback finished.")  

    except Exception as e:  
        print(f"Error playing audio: {e}")  


def main():  
    # 初始化 PyAudio 实例  
    pyaudio_instance = pyaudio.PyAudio()  

    try:  
        # 列出所有音频设备  
        list_audio_devices(pyaudio_instance)  

        # 选择设备  
        device_index = int(input("Enter the device index to test: "))  

        # 检测设备支持的采样率  
        supported_rates = get_supported_sample_rates(pyaudio_instance, device_index)  

        if not supported_rates:  
            print("No supported sample rates found for this device.")  
            return  

        # 选择一个采样率  
        print("\nSupported sample rates:", supported_rates)  
        sample_rate = int(input("Enter the sample rate to use (choose from the supported rates): "))  

        if sample_rate not in supported_rates:  
            print("Invalid sample rate selected.")  
            return  

        # 播放音频  
        play_audio_stream(pyaudio_instance, device_index, sample_rate)  

    finally:  
        # 释放 PyAudio 资源  
        pyaudio_instance.terminate()  


if __name__ == "__main__":  
    main()