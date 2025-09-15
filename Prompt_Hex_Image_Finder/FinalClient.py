### Description ###
# The client is the way in which the user will interact with the server.
# It uses the Openai API key along with the GPT-4o model

# Importing Required Packages
import asyncio
import json
import os
import time
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import streamlit as st

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Function to Convert a hexcode into RGB format
def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip("#")
    return tuple(int(hexcode[i:i + 2], 16) for i in (0, 2, 4))

# Function for Measureing distance between two rgb colors
def color_distance(rgb1, rgb2):
    return sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5

# Function to find the laminates in sorted manner
def find_all_laminates_sorted(input_hexcode, laminate_data):
    """Find all laminates sorted by color distance for the given hexcode."""
    input_rgb = hex_to_rgb(input_hexcode)
    ranked = []
    seen_names = set()

    for texture in laminate_data:
        tex_hex_list = texture.get("hexcode", [])
        if not isinstance(tex_hex_list, list) or not tex_hex_list:
            continue

        try:
            distances = [color_distance(input_rgb, hex_to_rgb(h)) for h in tex_hex_list if h.startswith("#")]
            if not distances:
                continue
            min_distance = min(distances)
        except Exception:
            continue

        name = texture.get("name", "")
        if name in seen_names:
            continue

        ranked.append({
            "name": name,
            "sku": texture.get("sku", ""),
            "link": f"https://dummynavigator.centuryply.com/product-details/{texture.get('id')}",
            "distance": min_distance
        })
        seen_names.add(name)

    ranked.sort(key=lambda x: x["distance"])
    return ranked

# Function to process the next batch so that the wait is minimized
def get_next_batch(hexcode, laminate_data, batch_size=4):
    """Get the next batch of laminates for the given hexcode."""
    if "shown_laminates" not in st.session_state:
        st.session_state["shown_laminates"] = {}

    if hexcode not in st.session_state["shown_laminates"]:
        # Initialize for this color
        sorted_laminates = find_all_laminates_sorted(hexcode, laminate_data)
        st.session_state["shown_laminates"][hexcode] = {"index": 0, "sorted": sorted_laminates}

    data = st.session_state["shown_laminates"][hexcode]
    start = data["index"]
    end = start + batch_size
    data["index"] = end
    return data["sorted"][start:end]

# Memory Initialization in Streamlit
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "last_hexcode" not in st.session_state:
    st.session_state["last_hexcode"] = None
if "shown_laminates" not in st.session_state:
    st.session_state["shown_laminates"] = {}

# Defining a Async function to create the Agentic Behavior
async def modified_laminate_agent(user_prompt: str):
    try:
        # Detect "other options" requests
        ask_more = "other option" in user_prompt.lower() or "more" in user_prompt.lower()

        # Load laminate JSON
        with open("laminates.json", "r") as f:
            laminate_data = json.load(f)

        laminate_data = laminate_data.get("laminates", [])

        hexcode = None
        response_text = ""

        if ask_more and st.session_state["last_hexcode"]:
            # Use last hexcode to fetch next batch
            hexcode = st.session_state["last_hexcode"]
            response_text = f"Showing more options for color {hexcode}."
        else:
            # Run agent to find new hexcode
            client = MultiServerMCPClient({
                "LaminateFinder": {
                    "command": "python",
                    "args": ["Finalserver.py"],
                    "transport": "stdio",
                }
            })

            tools = await client.get_tools()
            # model = ChatGroq(model="qwen/qwen3-32b", max_tokens=4000)
            model = ChatOpenAI(model = "gpt-4o", max_tokens = 4000)
            agent = create_react_agent(model, tools)

            fixed_prompt = (
                # "Give me only one hexcode for the following phrase of the dominant color in json "
                # "with a key of hexcode and key of the description that you want to show the user "
                # "but it shouldn't be white or black with no additional text - "
                "Return ONLY valid JSON. Do not add any text, markdown, or explanation. "
                "The JSON must have exactly two keys: 'hexcode' and 'description'. "
                "Hexcode must start with # and must not be white (#FFFFFF) or black (#000000). "
                "Example: {\"hexcode\": \"#AABBCC\", \"description\": \"Soft blue shade\"}. "
                "Now extract for: "
            )

            # Build messages with history
            past_messages = []
            for msg in st.session_state["chat_history"]:
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                past_messages.append({"role": role, "content": msg.content})

            phrase = f"{fixed_prompt}{user_prompt}"
            past_messages.append({"role": "user", "content": phrase})

            response = await agent.ainvoke({"messages": past_messages})
            result = response["messages"][-1].content

            try:
                color_info = json.loads(result)
                hexcode = color_info.get("hexcode")
                description = color_info.get("description", "Found matching color.")

                hexcode = hexcode.upper() if hexcode else None

                response_text = f"""
                    <div style="font-size:20px; margin-bottom:10px;">
                    <b>Description:</b> {description}<br>
                    <b>Hex Code:</b> <span style="color:green;">{hexcode}</span>
                    </div>
                """
            except json.JSONDecodeError:
                st.error("Error: Invalid JSON from agent.")
                return None

            st.session_state["last_hexcode"] = hexcode
            st.session_state["shown_laminates"][hexcode] = {
                "index": 0,
                "sorted": find_all_laminates_sorted(hexcode, laminate_data)
            }

        if not hexcode:
            st.error("Hexcode not found.")
            return None

        # Get next batch of laminates
        top_matches = get_next_batch(hexcode, laminate_data, batch_size=4)
        final_result = {"matchedLaminates": top_matches}

        # Display response
        st.write("### **Laminate Agent Response**")
        st.markdown(response_text, unsafe_allow_html = True)

        if final_result and "matchedLaminates" in final_result:
            st.markdown("## **Matched Laminates:**")
            for i, lam in enumerate(final_result["matchedLaminates"], start=1):
                st.markdown(
                    f"""
                    <div style='font-size:22px; font-weight:bold;'>{i}. {lam['name']}</div>
                    <ul style='font-size:19px; margin-top: 0;'>
                        <li>SKU: {lam['sku']}</li>
                        <li><a href='{lam['link']}' target='_blank'>View Details</a></li>
                    </ul>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.write("No more options available.")

        # Add to memory
        st.session_state["chat_history"].append(HumanMessage(content = user_prompt))
        st.session_state["chat_history"].append(AIMessage(content = response_text))

        return final_result

    except Exception as e:
        st.error(f"Unexpected error: {e}")