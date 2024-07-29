from openai import OpenAI

client = OpenAI()

file = client.files.create(
    file=open("other.json", "rb"),
    purpose='assistants',
)


assistant = client.beta.assistants.create(
    name="SwipBot",
    instructions="Eres un agente personal de ventas. Examinas y respondes a las preguntas que se te envien de acuerdo a los productos.",
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}],
    tool_resources={
        "code_interpreter": {
            "file_ids":[file.id]
        }
    }
)


thread = client.beta.threads.create()

messsage = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="",
)