import os
import json
import httpx
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import ast  # For safely parsing list strings

# ------------------------------------------------------------------
# 1. CONFIGURATION & SETUP
# ------------------------------------------------------------------

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="TownManor.ai Assistant",
    page_icon="🏡",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .property-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    div[data-testid="stImage"] img {
        border-radius: 10px;
        max-height: 200px;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "tngtech/deepseek-r1t2-chimera:free"
PROPERTY_API_URL = "https://www.townmanor.ai/api/property"

# ------------------------------------------------------------------
# 2. DATA FETCHING & LOGIC
# ------------------------------------------------------------------

@st.cache_data(ttl=3600)
def fetch_properties():
    """Fetch all properties from TownManor API and cache them."""
    try:
        # Use httpx for robust HTTP requests
        response = httpx.get(PROPERTY_API_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        else:
            st.error(f"Unexpected API response format: {type(data)}")
            return []
    except Exception as e:
        st.error(f"Failed to load properties: {e}")
        return []

def clean_slug(text):
    """Create a slug from property name for URLs."""
    if not text:
        return ""
    # Simple slugify: lowercase, replace spaces with hyphens, remove special chars
    slug = "".join(c if c.isalnum() or c.isspace() else "" for c in text)
    return "-".join(slug.lower().split())

def get_unique_cities(properties):
    """Extract unique city names."""
    cities = set()
    for p in properties:
        val = p.get('city')
        if val and str(val).lower() != 'nan':
            # normalize casing
            cities.add(str(val).strip().title())
    return sorted(list(cities))

def filter_properties(query, properties):
    """
    Filter properties by City or Property Name.
    Returns: (results, detected_city)
    """
    query = query.lower().strip()
    if not query:
        return [], None
    
    results = []
    seen_ids = set()
    detected_cities = {} # Count occurrences of cities in results
    
    for p in properties:
        pid = p.get('id')
        if pid in seen_ids:
            continue
            
        # Fields to search in
        p_city = str(p.get('city', '')).strip()
        p_name = str(p.get('property_name', '')).strip()
        p_addr = str(p.get('address', '')).strip()
        
        # Check for matches
        if query in p_city.lower() or query in p_name.lower() or query in p_addr.lower():
            results.append(p)
            seen_ids.add(pid)
            
            # Track city frequency to find the "dominant" city of this search
            if p_city and p_city.lower() != 'nan':
                 # Normalize city name casing for counting
                 c_key = p_city.title()
                 detected_cities[c_key] = detected_cities.get(c_key, 0) + 1

    # Determine the most relevant city found in the results
    dominant_city = None
    if detected_cities:
        dominant_city = max(detected_cities, key=detected_cities.get)
    
    # Fallback: exact match if query is a city name
    if not dominant_city:
        for c in get_unique_cities(properties):
            if c.lower() == query:
                dominant_city = c
                break

    return results, dominant_city

# Load Data on Startup
ALL_PROPERTIES = fetch_properties()
UNIQUE_CITIES = get_unique_cities(ALL_PROPERTIES)

# System Prompt
services_info = """
TownManor.ai Services:
1. Search Property: https://townmanor.ai/search-property
2. List Your Property: https://townmanor.ai/landlord
3. Rent Agreement: https://townmanor.ai/rentagreements
4. Commercial Investment: https://townmanor.ai/commercial
5. Home Loan: https://townmanor.ai/homeloan
6. Home Interior: https://townmanor.ai/homeinteriornew
7. Home Shifting: https://townmanor.ai/shift
8. RERA Verification: https://townmanor.ai/reraverificationpage
"""

base_system_prompt = (
    f"You are the TownManor.ai Assistant.\n"
    f"Cities: {', '.join(UNIQUE_CITIES)}.\n"
    f"Services:\n{services_info}\n"
    f"Request Processing:\n"
    f"1. **Engage First**: Start with a warm, helpful summary of what you found. Use emojis (🏡, ✨, 📍). Give a nice writeup about the city/property.\n"
    f"2. **Then Provide Links**: After the summary, provide the direct links.\n"
    f"3. **City Search**: If exploring a city (e.g. Gurgaon), mention its key features briefly, then give: https://townmanor.ai/adminproperty/Gurgaon\n"
    f"4. **Tone**: Friendly, professional, and helpful. Not robotic."
)

# ------------------------------------------------------------------
# 3. UI & CHAT INTERFACE
# ------------------------------------------------------------------

st.title("🏡 TownManor.ai Assistant")

if not API_KEY:
    st.warning("⚠️ OPENROUTER_API_KEY not found in environment variables. Please check your .env file.")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": base_system_prompt},
        {"role": "assistant", "content": "Namaste! ✨ I am your TownManor AI. I can find your dream home in Gurgaon, Noida, Goa, and more! 🏡 Try asking about 'Maa Bhagwati' or 'Flats in Noida'."}
    ]

# Display Chat History
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle User Input
if prompt := st.chat_input("Ask me anything..."):
    
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Search Logic
    ignore_words = {'hi', 'hello', 'hey', 'namaste', 'hola', 'greetings', 'test'}
    
    if prompt.lower().strip() in ignore_words:
        matched_results, dominant_city = [], None
    else:
        matched_results, dominant_city = filter_properties(prompt, ALL_PROPERTIES)
    
    # 3. Context Injection
    context_note = ""
    
    if matched_results:
        props_data = []
        for p in matched_results[:5]: 
            slug = clean_slug(p.get('property_name', ''))
            pid = p.get('id')
            deep_link = f"https://townmanor.ai/en/newadminpage/{pid}/{slug}"
            props_data.append(f"- {p.get('property_name')} ({p.get('city')}) -> {deep_link}")
        
        props_str = "\n".join(props_data)
        
        context_note = f"\n[SYSTEM: Found properties:\n{props_str}\n"
        
        if dominant_city:
            city_link = f"https://townmanor.ai/adminproperty/{dominant_city}"
            context_note += f"User searching in {dominant_city}. Summarize the options nicely and then Recommend link: {city_link}]"
    else:
        context_note = "" 

    # Prepare messages 
    messages_for_api = st.session_state.messages + [{"role": "system", "content": context_note}]

    # 4. Generate AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
            
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages_for_api,
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

    # Save Assistant Response
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 5. Display Property Cards
    if matched_results:
        st.write("---")
        if dominant_city:
            st.markdown(f"### 🏘️ Properties in {dominant_city}")
            st.markdown(f"👉 **[View All in {dominant_city}](https://townmanor.ai/adminproperty/{dominant_city})**")
        
        # Grid Layout
        cols = st.columns(3)
        for idx, prop in enumerate(matched_results):
            with cols[idx % 3]:
                with st.container(border=True):
                    # Data preparation
                    pid = prop.get('id')
                    slug = clean_slug(prop.get('property_name', ''))
                    deep_link = f"https://townmanor.ai/en/newadminpage/{pid}/{slug}"
                    
                    # IMAGE HANDLING (Fixed for Arrays)
                    img_data = prop.get('image_repository')
                    final_img = None
                    
                    if img_data:
                        try:
                            # Check if it looks like a list string "['url1', 'url2']"
                            if isinstance(img_data, str) and img_data.strip().startswith('['):
                                # Safely evaluate string list
                                urls = ast.literal_eval(img_data)
                                if urls and isinstance(urls, list) and len(urls) > 0:
                                    final_img = urls[0]
                            elif isinstance(img_data, str) and 'http' in img_data:
                                final_img = img_data
                        except:
                            final_img = None 

                    if final_img:
                        st.image(final_img, use_container_width=True)
                    else:
                        st.text("No Image")

                    # Title & Price
                    st.markdown(f"**[{prop.get('property_name', 'Property')}]({deep_link})**")
                    st.markdown(f"<span style='color:green; font-weight:bold'>{prop.get('price', 'Call for Price')}</span>", unsafe_allow_html=True)
                    
                    # Details
                    loc = prop.get('locality') or prop.get('address') or prop.get('city')
                    st.caption(f"📍 {loc}")
                    
                    st.link_button("View Details", deep_link)
                    
                    with st.expander("Quick Info"):
                        desc = prop.get('description')
                        if desc:
                            st.write(desc[:200] + "...")
                        else:
                            st.write("No description available.")
                        st.write(f"**City:** {prop.get('city')}")
                        st.write(f"**Status:** {prop.get('construction_statu')}")
