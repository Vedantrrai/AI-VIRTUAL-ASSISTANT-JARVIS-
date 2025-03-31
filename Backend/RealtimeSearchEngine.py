from googlesearch import search
from json import load, dump
from datetime import datetime
from groq import Groq
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars["Username"]
Assistantname = env_vars["Assistantname"]
GroqAPIKey = env_vars["GroqAPIKey"]


if not GroqAPIKey:
    raise ValueError("GroqAPIKey not found in .env file.")


client = Groq(api_key=GroqAPIKey)


System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

try:
     with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
      with open(r"Data\ChatLog.json", "w") as f:
        dump([],f)


def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
    except Exception as e:
        return f"Error while performing search: {str(e)}"

    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer


def AnswerModifier(Answer):
    if isinstance(Answer, list):
        Answer = ''.join(Answer)

    lines = str(Answer).splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    data=""
    current_date_time = datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data = f"Use This real-time Information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load chat history
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": f"{prompt}"})

    # Add Google search results to system messages
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    # Generate response using Groq client
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""

    # Concatenate response chunks
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    # Clean up the response
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    # Save updated chat log
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    # Remove the last system message
    SystemChatBot.pop()

    return AnswerModifier(Answer=Answer)

# Main entry point
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
