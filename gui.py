import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import pyttsx3
import speech_recognition as sr
from gpt4all import GPT4All
import pyaudio
import wave
from faster_whisper import WhisperModel

class AudioProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Smart")

        self.root.geometry("600x400")  # Set the window size

        # Create the main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)  # Column 0 takes all available horizontal space

        # Create a label for audio recording
        self.audio_label = tk.Label(self.main_frame, text="Click 'Start' to begin listening...", font=("Helvetica", 12))
        self.audio_label.grid(row=0, column=0, pady=10, columnspan=2)

        # Create a text widget for GPT response
        self.gpt_response_text = tk.Text(self.main_frame, width=40, height=5, font=("Helvetica", 12))
        self.gpt_response_text.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.gpt_response_text.config(state=tk.DISABLED)  # Make the text widget read-only


        # Create buttons for audio
        self.start_audio_button = tk.Button(self.main_frame, text="Start Audio", command=self.start_audio_recording)
        self.start_audio_button.grid(row=1, column=0, padx=5, pady=5)
        self.stop_audio_button = tk.Button(self.main_frame, text="Stop Audio", state=tk.DISABLED, command=self.stop_audio_recording)
        self.stop_audio_button.grid(row=1, column=1, padx=5, pady=5)

        # Create a label for text input
        self.text_label = tk.Label(self.main_frame, text="Enter a prompt:", font=("Helvetica", 12))
        self.text_label.grid(row=2, column=0, sticky="w", padx=5)

        # Create a text entry field for user input
        self.text_entry = tk.Entry(self.main_frame, width=40, font=("Helvetica", 12))
        self.text_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # Create a button to process the text input
        self.process_text_button = tk.Button(self.main_frame, text="Chat", command=self.process_text)
        self.process_text_button.grid(row=3, column=1, padx=5, pady=5)

        # Create a lights section with ON and OFF buttons
        self.lights_label = tk.Label(self.main_frame, text="Lights Control:", font=("Helvetica", 12))
        self.lights_label.grid(row=5, column=0, sticky="w", padx=5)

        # Create ON and OFF buttons
        self.on_button = tk.Button(self.main_frame, text="ON", command=self.turn_lights_on)
        self.on_button.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.off_button = tk.Button(self.main_frame, text="OFF", command=self.turn_lights_off)
        self.off_button.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Create a doors section with LOCK and UNLOCK buttons
        self.doors_label = tk.Label(self.main_frame, text="Doors Control:", font=("Helvetica", 12))
        self.doors_label.grid(row=7, column=0, sticky="w", padx=5)

        # Create lock and unlock buttons
        self.lock_button = tk.Button(self.main_frame, text="LOCK", command=self.lock_doors)
        self.lock_button.grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.unlock_button = tk.Button(self.main_frame, text="UNLOCK", command=self.unlock_doors)
        self.unlock_button.grid(row=8, column=1, padx=5, pady=5, sticky="w")

        # Create a sound sensor with lights section with ON and OFF buttons
        self.soundlights_label = tk.Label(self.main_frame, text="Sound triggers", font=("Helvetica", 12))
        self.soundlights_label.grid(row=9, column=0, sticky="w", padx=5)

        # Create ACTIVATE and DEACTIVATE buttons
        self.activatelights_button = tk.Button(self.main_frame, text="LIGHTS", command=self.activate_lights)
        self.activatelights_button.grid(row=10, column=0, padx=5, pady=5, sticky="w")
        self.activatealarm_button = tk.Button(self.main_frame, text="ALARM", command=self.activate_alarm)
        self.activatealarm_button.grid(row=10, column=1, padx=5, pady=5, sticky="w")

        

        # Create a label for temperature threshold
        self.threshold_label = tk.Label(self.main_frame, text="Set Threshold Temperature:", font=("Helvetica", 12))
        self.threshold_label.grid(row=11, column=0, pady=10, sticky="w")

        # Create a scale for setting the threshold temperature
        self.threshold_scale = ttk.Scale(self.main_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=200, command=self.update_real_time_value)
        self.threshold_scale.set(25)  # Set the default threshold to 25 degrees
        self.threshold_scale.grid(row=12, column=0, pady=5, sticky="w")

        # Create a label to display real-time value
        self.real_time_value_label = tk.Label(self.main_frame, text=f"Threshold: {self.threshold_scale.get()}°C", font=("Helvetica", 10))
        self.real_time_value_label.grid(row=13, column=1, pady=5, padx=10, sticky="w")

        # Create a button to update the threshold
        self.update_threshold_button = tk.Button(self.main_frame, text="Update Threshold", command=self.update_threshold)
        self.update_threshold_button.grid(row=14, column=0, pady=5)

        # Initialize the TTS engine
        self.engine = pyttsx3.init()

        # Create an instance of the Whisper model for audio transcription
        self.whisper_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
        # Create an instance of the GPT model for chat
        self.gpt_model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", allow_download=False)

        self.spoken_text = ""
        self.response = ""
        self.processing = False
        self.recording_audio = False
        self.mode = "LLM"

        
    
    def setup_serial_connection(self):
        ports = serial.tools.list_ports.comports()
        ports_list = [str(port) for port in ports]
        val = input('Select Port: COM')
        port_var = None

        for port in ports_list:
            if port.startswith(f'COM{val}'):
                port_var = f'COM{val}'
                break

        if port_var is None:
            print("Invalid COM port. Exiting...")
            exit(1)

        serial_inst = serial.Serial(port=port_var, baudrate=9600)
        return serial_inst


    def start_audio_recording(self):
        self.recording_audio = True
        self.audio_label.config(text="Recording audio... (Press 'Stop Audio' to finish)")
        self.start_audio_button.config(state=tk.DISABLED)
        self.stop_audio_button.config(state=tk.NORMAL)

        # Initialize PyAudio for audio recording
        audio_format = pyaudio.paInt16  # Adjust the format as needed
        channels = 1  # Mono
        sample_rate = 16000  # Adjust the sample rate as needed
        chunk_size = 1024  # Adjust the chunk size as needed
        audio_duration = 5  # Maximum duration for recording in seconds

        p = pyaudio.PyAudio()
        stream = p.open(format=audio_format, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk_size)

        audio_frames = []

        while self.recording_audio:
            print("Listening...")
            audio_frames = []

            for _ in range(0, int(sample_rate / chunk_size * audio_duration)):
                try:
                    audio_data = stream.read(chunk_size)
                    audio_frames.append(audio_data)
                except IOError:
                    print("IOError: Unable to record audio.")


            # Convert the recorded audio frames to a single byte string
            audio_data = b''.join(audio_frames)

            # Save the recorded audio to a WAV file
            audio_file = "recorded_audio.wav"
            with wave.open(audio_file, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(audio_format))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(audio_frames))
            
            print("Recognizing...")

            # Transcribe the saved audio file using Whisper
            segments, info = self.whisper_model.transcribe(audio_file, beam_size=5)

            for segment in segments:
                self.spoken_text = segment.text
            self.process_audio()
            self.root.update()  # Update the GUI

        self.stop_audio_button.config(state=tk.DISABLED)
        self.start_audio_button.config(state=tk.NORMAL)

    
    def stop_audio_recording(self):
        self.recording_audio = False
        self.audio_label.config(text="Recording audio stopped")
    
    def process_audio(self):
        print("Whisper thinks you said: " + self.spoken_text)
        if "tom" in self.spoken_text.lower():
            self.mode = "Arduino"
            self.audio_label.config(text="Arduino mode activated.")
            # Initialize the serial connection to the Arduino
            self.serial_inst = self.setup_serial_connection()
            self.speak_response("Arduino mode activated. Please say a command.")
        elif "julie" in self.spoken_text.lower():
            self.mode = "LLM"
            self.audio_label.config(text="Chat mode activated.")
            self.speak_response("Chat mode activated.")
            serial.Serial(port="COM4", baudrate=9600).close()
        else:
            if self.mode == "Arduino":
                # Send the spoken text as a command to the Arduino
                self.audio_label.config(text="Sending command to Arduino: " + self.spoken_text)
                command = self.spoken_text.upper()
                self.serial_inst.write(command.encode('utf-8'))
            elif self.mode == "LLM":
                chat_session_prompt = 'You are an AI assistant that follows instructions extremely well.Your name is Julie. Help as much as you can.'
                chat_session_prompt += '### Instruction:\n{0}\n### Response:\n'
                with self.gpt_model.chat_session(chat_session_prompt):
                    response = self.gpt_model.generate(self.spoken_text, temp=0)
                    self.response = response
                    #self.audio_label.config(text="Julie says (from audio): " + response)
                    self.speak_response(response)
                    # Update the GPT response text widget
                    self.gpt_response_text.config(state=tk.NORMAL)
                    self.gpt_response_text.delete("1.0", tk.END)  # Clear the previous content
                    self.gpt_response_text.insert(tk.END, response)
                    self.gpt_response_text.config(state=tk.DISABLED)



    def process_text(self):
        user_input = self.text_entry.get()

        if user_input:
            if "tom" in user_input.lower():
                self.mode = "Arduino"
                self.audio_label.config(text="Arduino mode activated.")
                # Initialize the serial connection to the Arduino
                self.serial_inst = self.setup_serial_connection()
                self.speak_response("Welcome to your smart home. What can I do for you?")
            elif "julie" in user_input.lower():
                self.mode = "LLM"
                self.audio_label.config(text="Chat mode activated.")
                self.speak_response("Chat mode activated.")
                #serial.Serial(port="COM4", baudrate=9600).close()
            else:
                if self.mode == "Arduino":
                    # Send the spoken text as a command to the Arduino
                    self.audio_label.config(text="Sending command to Arduino: " + self.spoken_text)
                    command = user_input.upper()
                    self.serial_inst.write(command.encode('utf-8'))
                elif self.mode == "LLM":
                    chat_session_prompt = 'You are an AI assistant that follows instructions extremely well.Your name is Julie. Help as much as you can.'
                    chat_session_prompt += '### Instruction:\n{0}\n### Response:\n'
                    with self.gpt_model.chat_session(chat_session_prompt):
                        response = self.gpt_model.generate(user_input, temp=0)
                        self.response = response
                        #self.audio_label.config(text="Julie says (from audio): " + response)
                        self.speak_response(response)
                        # Update the GPT response text widget
                        self.gpt_response_text.config(state=tk.NORMAL)
                        self.gpt_response_text.delete("1.0", tk.END)  # Clear the previous content
                        self.gpt_response_text.insert(tk.END, response)
                        self.gpt_response_text.config(state=tk.DISABLED)
        else:
            self.audio_label.config(text="Please enter a prompt in the text field.")
    
    def speak_response(self, response_text):
        voices = self.engine.getProperty('voices')
        rate = self.engine.getProperty('rate')
        if self.mode == "Arduino":
            self.engine.setProperty('voice', voices[0].id)
        else:
            self.engine.setProperty('voice', voices[1].id)
        self.engine.setProperty('rate', 170) 

        
        self.engine.say(response_text)
        self.engine.runAndWait()
    
    def turn_lights_on(self):
        command = "ON"
        self.serial_inst.write(command.encode('utf-8'))
        self.on_button.config(state=tk.DISABLED)
        self.off_button.config(state=tk.NORMAL)
        self.speak_response("Lights turned on")
    
    def turn_lights_off(self):
        command = "OFF"
        self.serial_inst.write(command.encode('utf-8'))
        self.on_button.config(state=tk.NORMAL)
        self.off_button.config(state=tk.DISABLED)
        self.speak_response("Lights turned off")

    def lock_doors(self):
        command = "LOCK"
        self.serial_inst.write(command.encode('utf-8'))
        self.lock_button.config(state=tk.DISABLED)
        self.unlock_button.config(state=tk.NORMAL)
        self.speak_response("Doors locked")
    
    def unlock_doors(self):
        command = "UNLOCK"
        self.serial_inst.write(command.encode('utf-8'))
        self.lock_button.config(state=tk.NORMAL)
        self.unlock_button.config(state=tk.DISABLED)
        self.speak_response("Doors unlocked")

    def activate_lights(self):
        command = "ACTIVATE LIGHTS"
        self.serial_inst.write(command.encode('utf-8'))
        self.activatelights_button.config(state=tk.DISABLED)
        self.activatealarm_button.config(state=tk.NORMAL)
        self.speak_response("Lights will turn on when sound is detected")
    
    def activate_alarm(self):
        command = "ACTIVATE ALARM"
        self.serial_inst.write(command.encode('utf-8'))
        self.activatelights_button.config(state=tk.NORMAL)
        self.activatealarm_button.config(state=tk.DISABLED)
        self.speak_response("Alarm will go off when sound is detected")

    def update_real_time_value(self, value):
        # Update the label to show the real-time value
        self.real_time_value_label.config(text=f"Threshold: {value}°C")

    def update_threshold(self):
        # Update the threshold temperature based on the scale value
        self.threshold_temperature = round(self.threshold_scale.get())
        print(f"Threshold Temperature updated to {self.threshold_temperature} degrees.")
        command = f"SET_THRESHOLD {self.threshold_temperature}"
        self.serial_inst.write(command.encode('utf-8'))
        self.speak_response(f"I will turn on the fan if the temperature goes beyond {self.threshold_temperature} degrees.")




if __name__ == "__main__":
    root = tk.Tk()
    app = AudioProcessingApp(root)
    root.mainloop()

