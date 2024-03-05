from gpt4all import GPT4All
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", allow_download=False)
tokens = []
for token in model.generate("The capital of France is", max_tokens=20, streaming=True):
    tokens.append(token)
print(tokens)

def speak_response(self, response_text):
    voices = self.engine.getProperty('voices')
    rate = self.engine.getProperty('rate')   # getting details of current speaking rat
    self.engine.setProperty('voice', voices[1].id)
    self.engine.setProperty('rate', 170) 

    
    self.engine.say(response_text)
    self.engine.runAndWait()