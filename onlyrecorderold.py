import pyaudio
import wave
import os
import threading
import tkinter as tk
from tkinter import messagebox

class AudioRecorderThread(threading.Thread):
    def __init__(self, filename, indicator_label):
        super(AudioRecorderThread, self).__init__()
        self.filename = filename
        self.indicator_label = indicator_label
        self.stop_event = threading.Event()

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)

        frames = []

        while not self.stop_event.is_set():
            data = stream.read(1024)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

    def stop_recording(self):
        self.stop_event.set()
i = 1
#
recorder = False
#
def start_recording():
    global recorder
    global filename
    global i
    if recorder:
        messagebox.showinfo("Informativo", "Já havia gravação em andamento.")
    else:
        while os.path.exists(f'output{i}.wav' ):
            i += 1
        filename = f'output{i}.wav'
        indicator_label.config(text="Recording: ON", bg="red")  # Change indicator appearance
        recorder = AudioRecorderThread(filename, indicator_label)
        recorder.start()

def stop_recording():
    global recorder
    global filename
    if recorder:
        recorder.stop_recording()
        recorder.join()
        indicator_label.config(text="Recording: OFF", bg="green")  # Change indicator appearance
        messagebox.showinfo("Informativo", f'Áudio salvo como "{filename}".')
        #tk.messagebox.showinfo("Information", "Textinho")
        recorder = False
    else:
        messagebox.showinfo("Informativo", "Não havia gravação em andamento.")



root = tk.Tk()
root.title("Audio Recorder")
root.geometry("300x150")

start_button = tk.Button(root, text="Start Recording", command=start_recording)
stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)

indicator_label = tk.Label(root, text="Recording: OFF", bg="green")

start_button.pack()
stop_button.pack()
indicator_label.pack()

root.mainloop()