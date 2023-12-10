import streamlit as st
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

# Define headers with a User-Agent to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

def request_url(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.error(f"Error fetching URL: {e}")
        return None

def ImageAudit(url):
    response = request_url(url)
    if not response:
        return {"error": "Failed to retrieve content for image audit"}

    soup = BeautifulSoup(response.text, 'html.parser')
    img_elements = [img for img in soup.find_all('img') if img.get('src')]

    missing_alt = []
    broken_imgs = []

    base_domain = urlparse(url).netloc

    for img in img_elements:
        # Check for missing alt attributes
        if not img.get('alt'):
            missing_alt.append(urljoin(url, img['src']))

        # Check for internal broken images
        img_src = urljoin(url, img['src'])
        if base_domain in urlparse(img_src).netloc:
            img_response = request_url(img_src)
            if not img_response:
                broken_imgs.append(img_src)

    return {
        "missing_alt": (missing_alt, "Images should have alt attributes for accessibility and SEO."),
        "broken_imgs": (broken_imgs, "Broken images can lead to poor user experience.")
    }

st.title("Image Audit Tool")
url = st.text_input("Enter URL of the page to audit")

if url:
    with st.spinner("Auditing Images..."):
        image_audit_results = ImageAudit(url)
        for key, value in image_audit_results.items():
            st.write(f"**{value[1]}**")
            for img in value[0]:
                st.write(f"Image: {img}")
            st.write("---")

st.markdown("----")

# Add the "Made by [Your Name]" in the sidebar with a link
st.sidebar.markdown(
    "#### Made by [Your Name](https://yourwebsite.com)"
)
