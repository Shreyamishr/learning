import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config (Must be first)
st.set_page_config(
    page_title="TownManor.ai Assistant",
    page_icon="🏡",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .user-avatar {
        background-color: #4CAF50;
    }
    .bot-avatar {
        background-color: #2196F3;
    }
    h1 {
        color: #d4af37; /* Gold color for TownManor branding */
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# CONFIGURATION & LOGIC
# ------------------------------------------------------------------

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "tngtech/deepseek-r1t2-chimera:free"

# Service Info & System Prompt (SAME AS CLI VERSION)
services_info = """
TownManor.ai Services & URLs:
1. Search Property (Property search): https://townmanor.ai/search-property
2. List Your Property (Landlords/Owners): https://townmanor.ai/landlord
3. Rent Agreement: https://townmanor.ai/rentagreements
4. Commercial Investment: https://townmanor.ai/commercial
5. Home Loan: https://townmanor.ai/homeloan
6. Home Interior: https://townmanor.ai/homeinteriornew
7. Home Shifting: https://townmanor.ai/shift
8. RERA Verification: https://townmanor.ai/reraverificationpage
9. Land Verification: https://townmanor.ai/landverification
10. Credit Score: https://townmanor.ai/credit-score-new

Partner: Ovika Living (Short term rentals): https://www.ovikaliving.com/

Supported Cities for Direct Links:
Noida, Delhi, Gurgaon, Faridabad, Chandigarh, Jaipur, Lucknow, Sonipat, Dehradun, Patna, Indore, Agra, Varanasi, Guwahati, Ahmedabad, Goa, Uttarkhand, Bhubaneswar, Dubai, Qatar, Saudi (KSA), Jeddah, Riyadh, Oman, Muscat, Spain, Benahavis, London(UK).
"""

system_prompt = (
    f"You are the official AI assistant for TownManor.ai.\n"
    f"Here is our list of services and supported cities:\n{services_info}\n"
    f"Rules:\n"
    "1. **Smart City Routing (CRITICAL)**: If user asks for property in a specific CITY, provide https://townmanor.ai/adminproperty/<CityName>.\n"
    "2. **Property Name Recognition**: If user asks for a specific BUILDING/PROJECT name (e.g., 'Spaze Edge', 'Godrej Woods'):\n"
    "   - **STEP 1**: Use your internal knowledge to identify which CITY that property is in.\n"
    "   - **STEP 2**: Provide the link for THAT city. (e.g., Spaze Edge is in Gurgaon -> give /adminproperty/Gurgaon).\n"
    "   - **STEP 3**: Only if you are 100% sure the city is NOT in our supported list, or you cannot find the city, then default to /adminproperty/Noida.\n"
    "3. **Generic Search**: If query is generic (e.g. '3BHK flat') without city, default to https://townmanor.ai/adminproperty/Noida AND https://townmanor.ai/search-property.\n"
    "4. **Language**: responses must be CONCISE (short) and in HINGLISH/English. NO Devanagari script.\n"
    "5. Do not hallucinate URLs."
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Namaste! Main TownManor.ai assistant hoon. Batayein main aapki property search ya services me kaise madad kar sakta hoon? 🏡"}
    ]

# ------------------------------------------------------------------
# UI LAYOUT
# ------------------------------------------------------------------

st.title("🏡 TownManor.ai Assistant")
st.write("Your AI Partner for Real Estate | Buy, Rent, Sell & More")

# Display Chat History
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about properties, loans, or services..."):
    # User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
            
            # Make API Call
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=st.session_state.messages,
                extra_headers={
                    "HTTP-Referer": "https://townmanor.ai",
                    "X-Title": "TownManor.ai Assistant",
                }
            )
            
            full_response = completion.choices[0].message.content
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"⚠️ Error: {str(e)}"
            message_placeholder.error(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
