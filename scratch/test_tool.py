from google import genai
from google.genai import types
from app.agent.tool_executor import ALL_AGENT_TOOLS

# Initialize client
client = genai.Client(api_key="TEST")

# Let's inspect how the SDK processes tools
# We can create a dummy config with tools
config = types.GenerateContentConfig(
    tools=ALL_AGENT_TOOLS
)

print("Tools in config:")
for tool in config.tools:
    print(type(tool))
    print(tool)
