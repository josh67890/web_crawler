import os, sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlretrieve

# Create a folder to store images, if does not exist
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# Function to fetch and download all images from a webpage, and collect all lhyperlinks from page for further scanning
def download_images(url, folder_name="images", downloaded = set(), links = set()):
    try:
        create_folder(folder_name)
        count = 0

        # Send an HTTP request to the URL
        response = requests.get(url)
        response.raise_for_status()  

        soup = BeautifulSoup(response.text, 'html.parser')

        # proccess all images from page
        images = soup.find_all('img')
        
        for img in images:
            _img_url = img.get('src')
            if _img_url:
                img_name = _img_url[max(0, _img_url.rfind("/"))+1:]  # this will be the image name in the folder. could have issues if different images have same name
                try:
                    # Convert relative URLs to absolute ones
                    img_url = urljoin(url, _img_url)

                    if img_url not in downloaded:    # prevents redundances

                        # Extract the image filename from the url for storage in folder
                        img_filename = os.path.join(folder_name, img_name)

                        # Download the image and save it
                        print(f"Downloading {img_url}...")
                        urlretrieve(img_url, img_filename)

                        downloaded.add(img_url) # prevents redundances
                        count += 1
                except Exception as e:
                    print(e)
        

        print(f"Downloaded {count} images to the folder '{folder_name}' from the page {url}.")
        
        # Extract and save all full urls for further scanning
        hyperlinks = soup.find_all('a')
        for link in hyperlinks:
            href = link.get('href')
            if href and href.startswith(('http', 'https')):
                links.add(href)
            elif href and not href.startswith('#'):  # Handle relative URLs
                full_url = urljoin(url, href)
                links.add(full_url)
                
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")



def main():
    args = sys.argv[1:]
    while len(args) != 2: # user did not supply root url and depth of search
        print("\n\ntry again, this time type the full start url, and the depth for search/crawl (comma-seperated)\n")
        args = input().split()
    start_url, depth = args
    depth = int(depth)

    # determine working directory
    working_dir = input("\nto change the parent directory in which to store the downloaded images, enter the absoloute path here, otherwise hit 'enter/return':\n ")
    if working_dir == "":
        working_dir = os.getcwd()
    print(f"working parent directory in which the images will be stored: {working_dir}\n\n")


    visited = set() # records urls already visited
    downloaded_images = set() # records images already downloaded - stores the 
    links = {start_url} # holds all unique links to be crawled in current depth level 
    for _ in range(depth):
        new_links = set()  # collects unique links for scanning in next depth level
        for link in links:
            if link not in visited:
                visited.add(link)
                download_images(link, folder_name=working_dir+"/new_crawl_images_folder", downloaded=downloaded_images, links = new_links )
        links = new_links

if __name__ == "__main__":
    main()