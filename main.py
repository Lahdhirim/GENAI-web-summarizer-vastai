import logging
import os
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from src.web_scraper.web_scraper import WebScraper
from src.modeling.llm import LLMSelector
from src.config_loader.config_loader import config_loader
from src.utils.toolbox import load_prompt, send_email
from src.utils.schema import SessionStateSchema

@st.cache_resource
def load_config(config_path):
    return config_loader(config_path=config_path)

@st.cache_resource
def init_web_scraper(_config):
    return WebScraper(config=_config)

@st.cache_resource
def init_llm(_config):
    # load API keys from .env file
    load_dotenv(find_dotenv(), override=True)

    # Select the LLM provider based on the configuration
    selector = LLMSelector(config=_config)
    return selector.create_llm_from_config()

if __name__ == "__main__":

    # Set up logging
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(filename="logs/app.log",
                        level=logging.INFO,
                        filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    if SessionStateSchema.LOGGING_STARTED not in st.session_state:
        logging.info(f"Logging started at {logging.getLogger().name}")
        st.session_state[SessionStateSchema.LOGGING_STARTED] = True

    # Load the configuration
    config_path = "config/config.json"
    config = load_config(config_path=config_path)
    if SessionStateSchema.CONFIG_LOADED not in st.session_state:
        logging.info(f"Config loaded successfully from: {config_path}")
        st.session_state[SessionStateSchema.CONFIG_LOADED] = True

    # Initialize the web scraper
    web_scraper = init_web_scraper(_config=config.web_scraper_config)
    if SessionStateSchema.SCRAPER_INITIALIZED not in st.session_state:
        logging.info("Web scraper initialized successfully")
        st.session_state[SessionStateSchema.SCRAPER_INITIALIZED] = True
    
    # Initialize the LLM
    llm = init_llm(_config=config.llms_config)
    prompt = load_prompt(prompt_path=config.prompt_file)
    if SessionStateSchema.LLM_INITIALIZED not in st.session_state:
        logging.info(f"LLM {llm.__class__.__name__} initialized successfully")
        st.session_state[SessionStateSchema.LLM_INITIALIZED] = True

    # Streamlit UI
    st.title("🧠 Webpage Summarizer using LLMs")
    url = st.text_input("Enter a webpage URL to summarize:", placeholder="https://example.com")

    if url:
        with st.spinner("Fetching and parsing the page..."):
            page_text = web_scraper.fetch_text(url=url)
        logging.info(f"Page text fetched from: {url}")
        logging.info(f"Extracted content: {page_text}")

        # Summarize the content using the selected LLM
        if st.button(f"Summarize with LLM {llm.config.model} using {llm.__class__.__name__} provider"):
            with st.spinner("Generating summary using LLM..."):

                try:
                    summary = llm.call(content=page_text, prompt=prompt)
                    st.session_state[SessionStateSchema.SUMMARY] = summary
                    st.success("Summary generated successfully!")
                    logging.info(f"Summary generated: {summary}")

                except Exception as e:
                    
                    if "The daily request limit for OpenRouter has been reached" in str(e):
                        st.warning(str(e))
                        with open("assets/sleepy_robot.gif", "rb") as gif_file:
                            gif_bytes = gif_file.read()
                            st.image(gif_bytes, caption="Our summarizer needs a break...", use_container_width=True)
                    else:
                        st.error(f"Failed to generate summary: {e}")
    
    # [MEDIUM]: Treat the case where the URL is not valid
    else:
        st.warning("Please enter a valid webpage URL to summarize.")
        logging.info(f"No valid URL ({url}) provided for summarization.")


    # Display the generated summary if available
    if SessionStateSchema.SUMMARY in st.session_state:
        st.subheader("Summary")
        st.write(st.session_state[SessionStateSchema.SUMMARY])

        if st.button("Send Summary via Email"):
            st.session_state[SessionStateSchema.SEND_EMAIL_CLICKED] = True
    
    # Send the summary via email if desired
    if st.session_state.get(SessionStateSchema.SEND_EMAIL_CLICKED, False):
        with st.form("email_form"):
            recipient_email = st.text_input("Email address", placeholder="you@example.com")
            submitted = st.form_submit_button("Confirm and Send")
            if submitted:
                if recipient_email:

                    try:
                        send_email(
                            to_email=recipient_email,
                            subject="Summary from Web Scraper",
                            body=st.session_state[SessionStateSchema.SUMMARY]
                        )
                        st.success("Summary sent via email successfully!")
                        logging.info(f"Summary sent via email to {recipient_email}")
                        st.session_state[SessionStateSchema.SEND_EMAIL_CLICKED] = False

                    except Exception as e:
                        st.error("Failed to send summary via email")
                        logging.error(f"Email send to {recipient_email} failed: {e}")
                else:
                    st.warning("Please enter your email address.")