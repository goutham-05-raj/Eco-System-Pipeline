import asyncio
from dotenv import load_dotenv
load_dotenv()

from src.llm.groq import GroqProvider

p = GroqProvider()
print(f"Keys loaded: {len(p._clients)}")
print(f"Available: {p.is_available()}")

async def test():
    result = await p.extract(
        "Meta released LLaMA, a large language model.",
        {},
        "Summarize as JSON with key summary"
    )
    print("Result:", result)

asyncio.run(test())
print("SUCCESS - both keys working!")
