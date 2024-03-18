import openai
client = openai.OpenAI(
    api_key="anything",
    base_url="http://localhost:4000"
)

# request sent to model set on litellm proxy, `litellm --model`
response = client.chat.completions.create(model="gpt-3.5-turbo", messages = [
    {
        "role": "user",
        "content": "this is a test request, write a short poem"
    }
])

print(response)
print("-------------")
print(response.choices[0].message.content)