import streamlit as st
import logging
import os
from src.web_scraper.web_scraper import WebScraper
from src.config_loader.config_loader import config_loader

if __name__ == "__main__":

    # Load the configuration
    config_path = "config/config.json"
    config = config_loader(config_path=config_path)

    web_scraper = WebScraper(config=config.web_scraper_config)

    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(filename="logs/app.log",
                        level=logging.INFO,
                        filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s"
    )


    # Streamlit UI
    st.title("🧠 Webpage Summarizer using LLMs")
    url = st.text_input("Enter a webpage URL to summarize:", placeholder="https://example.com")

    if url:
        with st.spinner("Fetching and parsing the page..."):
            page_text = web_scraper.fetch_text(url=url)

        logging.info(f"Page text fetched from: {url}")
        logging.info(f"Extracted content (truncated): {page_text[:300]}")
        
        st.subheader("Raw extracted content")
        st.text_area(
            "Extracted Text",
            page_text[:3000] + ("..." if len(page_text) > 3000 else ""),
            height=200,
            disabled=True
        )