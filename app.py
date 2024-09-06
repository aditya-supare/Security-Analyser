import streamlit as st
import openai
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import re


load_dotenv()


firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')



firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)
openai.api_key = openai_api_key


def check_insecure_content(content):
    insecure_elements = []
    if "http://" in content:
        insecure_elements.append("HTTP URLs detected. Use HTTPS for secure communication.")
    if re.search(r"(?i)\b(api_key|password|secret)\b", content):
        insecure_elements.append("Potential sensitive information exposure (API keys or passwords).")
    return insecure_elements


st.title("Security Analyzer for Websites")


url = st.text_input("Enter the URL of the website:")


action = st.selectbox("Choose Action", ["scrape", "crawl"])

if st.button("Analyze Security"):
    if not url:
        st.error("Please enter a URL.")
    else:
        try:
            st.write(f"Selected action: {action}")
            st.write(f"Attempting to retrieve content from: {url}")

            if action == "scrape":
                scrape_result = firecrawl_app.scrape_url(url, params={'formats': ['markdown']})
                content = scrape_result.get('markdown', '')
            else:
                crawl_status = firecrawl_app.crawl_url(
                    url, 
                    params={'limit': 100, 'scrapeOptions': {'formats': ['markdown']}}
                )
                content = crawl_status.get('markdown', '')

           
            if content:
                st.write("Content successfully retrieved.")
                st.write(content[:500] + '...') 

               
                st.subheader("Security Analysis")
                insecure_content = check_insecure_content(content)
                if insecure_content:
                    st.error("Security Issues Detected:")
                    for issue in insecure_content:
                        st.write(f"- {issue}")
                else:
                    st.success("No immediate security issues detected.")

                
                st.subheader("Security Improvement Suggestions")
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": "You are a security expert."},
                              {"role": "user", "content": f"Provide security improvement suggestions for the following content:\n\n{content}"}],
                    max_tokens=500
                )
                security_suggestions = response['choices'][0]['message']['content'].strip()
                st.write(security_suggestions)
                st.download_button("Download Security Suggestions", security_suggestions, file_name="security_suggestions.txt")

            else:
                st.error("No content found in the scrape/crawl result.")
        except Exception as e:
           
            st.error(f"An error occurred: {str(e)}")
            st.write("Exception details:", str(e))
