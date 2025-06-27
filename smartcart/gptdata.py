
from groq import Groq

client = Groq(api_key="")

# ----------------------------- Gita QA Logic -----------------------------
def get_data(prompt):



    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    return response.choices[0].message.content.strip()

def ask_gpt(desc,prompt):
    prompt = f"""You are a shopping assistant. Based on this product description:\n\n"{desc}"\n\nAnswer this customer question: "{prompt}" in simple terms.give only answer for what they  ask do not hilusinate."""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=100

    )
    return response.choices[0].message.content.strip()

