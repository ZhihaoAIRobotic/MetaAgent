import requests  
import re

def fetch_service_response(url):  
    # Base URL of the service  
    service_url = "https://md.dhr.wtf/"  
    
    # Construct request parameters  
    params = {  
        "url": url  
    }  
    
    try:  
        # Send GET request  
        response = requests.get(service_url, params=params)  
        
        # Check response status code  
        if response.status_code == 200:  
            markdown_content = response.text
            # Extract image URLs from markdown
            images = re.findall(r'!\[.*?\]\((.*?)\)', markdown_content)
            return markdown_content, images  # Return the markdown content and images
        else:  
            return f"Error: Received status code {response.status_code}", []  
    except requests.RequestException as e:  
        return f"Request failed: {e}", []  

# Example call  
if __name__ == "__main__":  
    # Replace with the URL you want to request  
    test_url = "https://github.com/ZhihaoAIRobotic/MetaAgent"  
    markdown_content, images = fetch_service_response(test_url)  
    print("Markdown Content:", markdown_content)
    print("Images:", images)