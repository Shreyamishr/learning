import os
import sys
from openai import OpenAI
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Initialize colorama for colored terminal output
init()
# Load environment variables
load_dotenv()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ... (rest of the functions remain the same)

def main():
    # Configuration
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    BASE_URL = "https://openrouter.ai/api/v1"
    MODEL_NAME = "tngtech/deepseek-r1t2-chimera:free"
    
    if not API_KEY:
        print(f"{Fore.RED}Error: OPENROUTER_API_KEY not found in .env file{Style.RESET_ALL}")
        return
    
    # Initialize Client
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
        )
    except Exception as e:
        print(f"{Fore.RED}Error initializing OpenAI client: {e}{Style.RESET_ALL}")
        return

    # Chat History - TownManor.ai Context
    # Chat History - TownManor.ai Context
    # Chat History - TownManor.ai Context
    # Chat History - TownManor.ai Context
    # Chat History - TownManor.ai Context
    # Chat History - TownManor.ai Context
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
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    clear_screen()
    print(f"{Fore.CYAN}================================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}           TownManor.ai AI Assistant             {Style.RESET_ALL}")
    print(f"{Fore.CYAN}================================================={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Model: tngtech/deepseek-r1t2-chimera:free{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Type 'exit' or 'quit' to end the chat.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}================================================={Style.RESET_ALL}\n")

    while True:
        try:
            # Get User Input
            user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
            
            if user_input.lower() in ['exit', 'quit']:
                print(f"\n{Fore.YELLOW}Goodbye from TownManor.ai!{Style.RESET_ALL}")
                break
            
            if not user_input.strip():
                continue

            # Add user message to history
            messages.append({"role": "user", "content": user_input})

            # Show loading indicator (simple)
            print(f"{Fore.CYAN}TownManor AI is thinking...{Style.RESET_ALL}", end='\r')

            # API Call
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://townmanor.ai",
                    "X-Title": "TownManor.ai Chatbot", 
                },
                model=MODEL_NAME,
                messages=messages
            )

            # Get Response
            ai_response = completion.choices[0].message.content
            
            # Clear the loading line
            sys.stdout.write("\033[K") 
            
            # Print AI Response
            print(f"\r{Fore.BLUE}TownManor AI: {Style.RESET_ALL}{ai_response}\n")

            # Add AI response to history for context
            messages.append({"role": "assistant", "content": ai_response})

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Chat interrupted. Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}An error occurred: {e}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
