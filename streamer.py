import pyaudio
import wave
import speech_recognition as sr
from faster_whisper import WhisperModel

model_size = "tiny.en"

# Initialize the Whisper model
print("loading whisper")
model = WhisperModel(model_size, device="cpu", compute_type="int8")
print("done loading whisper")
# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Set up PyAudio to record audio
audio_format = pyaudio.paInt16  # Adjust the format as needed
channels = 1  # Mono
sample_rate = 16000  # Adjust the sample rate as needed
chunk_size = 1024  # Adjust the chunk size as needed
audio_duration = 5  # Maximum duration for recording in seconds

p = pyaudio.PyAudio()
stream = p.open(format=audio_format, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk_size)

# Start an infinite loop to continuously record and transcribe audio
while True:
    print("Listening...")
    audio_frames = []

    for _ in range(0, int(sample_rate / chunk_size * audio_duration)):
        try:
            audio_data = stream.read(chunk_size)
            audio_frames.append(audio_data)
        except IOError:
            print("IOError: Unable to record audio.")

    print("Recognizing...")

    # Convert the recorded audio frames to a single byte string
    audio_data = b''.join(audio_frames)

    # Save the recorded audio to a WAV file
    audio_file = "recorded_audio.wav"
    with wave.open(audio_file, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(audio_format))
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)

    # Perform speech-to-text using Whisper
    segments, info = model.transcribe(audio_file, beam_size=5)

    for segment in segments:
        print(segment.text)

# Cleanup PyAudio and close the stream when done
stream.stop_stream()
stream.close()
p.terminate()
