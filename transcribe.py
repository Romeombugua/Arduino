import whisper
import time


model = whisper.load_model("tiny.en")
start_time = time.time()
result = model.transcribe("test3.m4a", fp16=False)

# Stop measuring time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(result["text"])
print(f"Time taken: {elapsed_time} seconds")