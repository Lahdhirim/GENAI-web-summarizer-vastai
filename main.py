import logging
import os
from dotenv import load_dotenv, find_dotenv
from src.web_scraper.web_scraper import WebScraper
from src.modeling.llm import LLMSelector
from src.config_loader.config_loader import config_loader
from src.utils.toolbox import load_prompt
import streamlit as st

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
    if "logging_started_logged" not in st.session_state:
        logging.info(f"Logging started at {logging.getLogger().name}")
        st.session_state["logging_started_logged"] = True

    # Load the configuration
    config_path = "config/config.json"
    config = load_config(config_path=config_path)
    if "config_loaded_logged" not in st.session_state:
        logging.info(f"Config loaded successfully from: {config_path}")
        st.session_state["config_loaded_logged"] = True

    # Initialize the web scraper
    web_scraper = init_web_scraper(_config=config.web_scraper_config)
    if "web_scraper_initialized_logged" not in st.session_state:
        logging.info("Web scraper initialized successfully")
        st.session_state["web_scraper_initialized_logged"] = True
    
    # Initialize the LLM
    llm = init_llm(_config=config.llms_config)
    prompt = load_prompt(prompt_path=config.prompt_file)
    if "llm_initialized_logged" not in st.session_state:
        logging.info(f"LLM {llm.__class__.__name__} initialized successfully")
        st.session_state["llm_initialized_logged"] = True

    # Streamlit UI
    st.title("🧠 Webpage Summarizer using LLMs")
    url = st.text_input("Enter a webpage URL to summarize:", placeholder="https://example.com")

    if url:
        with st.spinner("Fetching and parsing the page..."):
            page_text = web_scraper.fetch_text(url=url)
        logging.info(f"Page text fetched from: {url}")
        logging.info(f"Extracted content: {page_text}")

        # Summarize the content using the selected LLM
        if st.button("Summarize with LLM"):
            with st.spinner("Generating summary using LLM..."):
                try:
                    summary = llm.call(content=page_text, prompt=prompt)
                    st.success("Summary generated successfully!")
                    logging.info(f"Summary generated: {summary}")
                    # Display the summary
                    st.subheader("Summary")
                    st.write(summary)
                except Exception as e:
                    st.error(f"Failed to generate summary: {e}")
    
    # [MEDIUM]: Treat the case where the URL is not valid
    else:
        st.warning("Please enter a valid webpage URL to summarize.")
        logging.info(f"No URL provided for summarization.")