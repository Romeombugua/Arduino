import speech_recognition as sr
from gpt4all import GPT4All

# Step 1: Obtain audio input with Whisper ASR
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)

# recognize speech using Whisper
try:
    spoken_text = r.recognize_whisper(audio, language="english", model="tiny.en")
    print("Whisper thinks you said: " + spoken_text)
except sr.UnknownValueError:
    print("Whisper could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Whisper")

# Step 2: Use the transcribed text as a prompt for GPT-4
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", allow_download=False)

# Define a chat session with GPT-4
chat_session_prompt = 'You are an AI assistant that follows instructions extremely well. Your name is Julie. Help as much as you can.'
chat_session_prompt += '### Instruction:\n{0}\n### Response:\n'

# Step 3: Generate a response from GPT-4 based on the spoken text
with model.chat_session(chat_session_prompt):
    response = model.generate(spoken_text, temp=0)
    print("Julie says: " + response)
