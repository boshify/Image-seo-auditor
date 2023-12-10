import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai
from urllib.parse import urljoin, urlparse

# Initialize OpenAI with API key from Streamlit's secrets
openai.api_key = st.secrets["openai_api_key"]

# Define headers with a User-Agent to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

# Function to safely fetch a URL's content
def request_url(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.error(f"Error fetching URL: {e}")
        return None

# GPT-3 based function to get SEO insights for images
def get_gpt_image_insights(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an SEO expert specialized in image optimization."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'].strip()
    except openai.OpenAIError as e:
        st.error(f"OpenAI API returned an error: {e}")
        return ""

# Main image audit function
def ImageAudit(url):
    response = request_url(url)
    if not response:
        return {"error": "Failed to retrieve content for image audit"}

    soup = BeautifulSoup(response.text, 'html.parser')
    img_elements = soup.find_all('img')

    audit_results = []

    for img in img_elements:
        img_url = urljoin(url, img.get('src'))
        alt_text = img.get('alt')
        file_name = urlparse(img_url).path.split('/')[-1]

        # Assess alt text
        if not alt_text:
            alt_text_insight = get_gpt_image_insights(f"Suggest alt text for image: {file_name}")
            audit_results.append((img_url, "Missing alt text", alt_text_insight))
        else:
            improved_alt_text = get_gpt_image_insights(f"Improve alt text: {alt_text}")
            audit_results.append((img_url, "Existing alt text", improved_alt_text))

        # Assess file name
        if '-' not in file_name and '_' not in file_name:
            improved_file_name = get_gpt_image_insights(f"Suggest a more descriptive file name for: {file_name}")
            audit_results.append((img_url, "Non-descriptive file name", improved_file_name))

    return audit_results

# Streamlit app layout
st.title("Automated One-Click Image SEO Audit")
url = st.text_input("Enter the URL of the page for image audit")

if url:
    with st.spinner("Analyzing images..."):
        audit_results = ImageAudit(url)
        for img_url, issue_type, recommendation in audit_results:
            st.write(f"Image: {img_url}")
            st.write(f"Issue: {issue_type}")
            st.write(f"Recommendation: {recommendation}")
            st.write("---")

# Add footer
st.markdown("#### Made by [Your Name](https://yourwebsite.com)")
