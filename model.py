from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True
)

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    quantization_config=bnb_config,
    device_map={"": "cuda:0"}
)

prompt = """
[System]
You are an expert storyteller and creative writer. You always produce complete, well-structured narratives, with vivid descriptions, coherent plots, and satisfying endings. You never truncate your sentences or stop abruptly; if more text is needed, continue until the story is complete.

[User]
Write a single short story of about 800-1,000 words on the topic of “Imran Khan the Pakistani Politician” The story should:
• Introduce memorable characters  
• Establish the setting and conflict clearly  
• Develop rising action, climax, and resolution  
• Use rich sensory details and dialogue  
• Conclude with a thoughtful reflection or twist  

Give the story a title that captures its essence. The story should be engaging and thought-provoking, leaving the reader with a sense of closure and satisfaction. Use a formal tone and avoid slang or colloquial expressions. The story should be suitable for a general audience and not contain any explicit content or offensive language.

[Assistant]
"""

inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")


outputs = model.generate(
    **inputs,
    max_new_tokens=1024,
    temperature=0.8,
    top_p=0.9,
    repetition_penalty=1.1,
    do_sample=True,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id,
    pad_token_id=tokenizer.eos_token_id,
)

generated = outputs[0][ inputs["input_ids"].size(-1) : ].tolist()
story = tokenizer.decode(generated, skip_special_tokens=True)
print(story)