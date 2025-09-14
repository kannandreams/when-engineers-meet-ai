# pip install -U bitsandbytes
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

"""### A Note for Mac Users
This code will automatically detect your hardware.
If you have an Apple Silicon Mac (M1/M2/M3), it will try to use the 'mps' device.
Otherwise, it will fall back to the 'cpu'.
The quantization itself will happen on the CPU if no NVIDIA GPU is found.
"""

# The model we want to use: small, fast, and perfect for this demo.
model_id = "distilgpt2"

# 1. Load the tokenizer (this is the same for both models)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# 2. Load the FULL PRECISION (FP32) model
# We'll explicitly move it to the CPU

print("Loading full precision model (distilgpt2)...")
model_fp32 = AutoModelForCausalLM.from_pretrained(model_id)
model_fp32.to("cpu") # Move to CPU

# 3. Load the QUANTIZED (4-bit) model
# The `bitsandbytes` library handles this with a simple configurations.

print("\nLoading 4-bit quantized model (distilgpt2)...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",  # Use 'nf4' for CPU
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype="float16",
)
model_4bit = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"
)

# Let's check the memory footprint
# We calculate the memory usage for each model.

fp32_mem = model_fp32.get_memory_footprint()
q4_mem = model_4bit.get_memory_footprint()

print(f"\nFull Precision Model Memory: {fp32_mem / 1e6:.2f} MB")
print(f"4-bit Quantized Model Memory: {q4_mem / 1e6:.2f} MB")
print(f"Memory saved: {100 * (1 - q4_mem / fp32_mem):.2f}%")

# --- Let's test the output ---
prompt = "Quantization in deep learning is"
# We need to manually move the inputs to the correct device for the full model
inputs = tokenizer(prompt, return_tensors="pt").to("cpu")

# Generate text with the full model
output_fp32 = model_fp32.generate(**inputs, max_new_tokens=20)

print("\n--- Full Model Output ---")
print(tokenizer.decode(output_fp32[0], skip_special_tokens=True))

# For the quantized model
inputs_4bit = tokenizer(prompt, return_tensors="pt")
# Generate text with the quantized model
output_4bit = model_4bit.generate(**inputs_4bit, max_new_tokens=20)

print("\n--- Quantized Model Output ---")
print(tokenizer.decode(output_4bit[0], skip_special_tokens=True))

# Add sampling to avoid repetition in quantized output
output_4bit = model_4bit.generate(
    **inputs_4bit,
    max_new_tokens=20,
    do_sample=True,
    temperature=0.7,
    top_k=50,
    top_p=0.95
)

print("\n--- Quantized Model Output ---")
print(tokenizer.decode(output_4bit[0], skip_special_tokens=True))