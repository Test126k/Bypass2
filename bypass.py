import requests
from bs4 import BeautifulSoup

# Function to bypass URL shortener for inshorturl.com
def bypass_url_shortener():
    try:
        response = requests.get(short_url, allow_redirects=False)
        if response.status_code in (301, 302, 303, 307, 308):
            return response.headers['Location']
        soup = BeautifulSoup(response.text, 'lxml')
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            if 'url=' in content:
                return content.split('url=')[1]
        script = soup.find('script', text=lambda x: x and 'window.location' in x)
        if script:
            script_text = script.string
            if 'window.location' in script_text:
                return script_text.split('window.location=')[1].split(';')[0].strip("'\"")
        return short_url
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Dictionary to map supported websites to their bypass functions
SUPPORTED_WEBSITES = {
    "inshorturl.com": bypass_inshorturl,
    # Add more websites and their bypass functions here
}

# Function to bypass a URL
def bypass_url(short_url):
    for website, bypass_function in SUPPORTED_WEBSITES.items():
        if website in short_url:
            return bypass_function(short_url)
    return "Sorry, this URL shortener is not supported yet."
