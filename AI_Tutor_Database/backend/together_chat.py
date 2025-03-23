from together import Together

client = Together(api_key="3524c3a5bde0b9a8bd4120ad72ab2a049ebf88ca0b5dba2abc599445e668fd4b")

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    messages=[
        {"role": "system", "content": "You are a helpful AI tutor."},
        {"role": "user", "content": "Explain recursion in simple terms."}
    ],
    max_tokens=200,  # Set a reasonable limit
    temperature=0.7,
    top_p=0.7,
    top_k=50,
    repetition_penalty=1,
    stop=["<|eot_id|>", "<|eom_id|>"],
    stream=True
)

for token in response:
    if hasattr(token, 'choices') and token.choices:
        delta = token.choices[0].delta
        if hasattr(delta, 'content'):
            print(delta.content, end='', flush=True)
