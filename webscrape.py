from bs4 import BeautifulSoup as bs
from googlesearch import search
import requests
import asyncio
import httpx


class WebScraper:

    def __init__(self, url=""):

        if isinstance(url, list):
            self.pages = url
            self.url = url[0]

        elif isinstance(url, str):
            self.pages = [url]
            self.url = url

        else:
            self.url_type_error()

    def set_url(self, url: str):
        """Updates the objects single url attribute"""
        self.url = url

    def get_url(self):
        """Returns the objects currently active url"""
        return self.url

    def add_url(self, url: str):
        """Adds a new url to the list of urls"""
        self.pages.append(url)

    def set_pages(self, page_list: list):
        """Updates the objects list of urls to be scraped"""
        self.pages = page_list

    def get_html(self):
        """Gets raw html data from the objects url attribute"""
        web_page = requests.get(self.url)
        soup = bs(web_page.text, "html.parser")
        return soup.prettify()

    def get_txt(self, line_length=70):
        """Attempts to organize text from websites into neatly written pages. Needs more work"""

        punctuation = [".", "!", "?"]

        def remove_extra_space(text_body: str):
            last_char = ""
            new_text = ""

            for char in text_body:
                if char == "\xa0" or char == "\n":
                    char = " "

                if last_char == " " and char == " ":
                    char = ""

                new_text += char

                if char != "":
                    last_char = char

            return new_text

        def make_neat(text_body: list):

            words = remove_extra_space(" ".join(text_body))
            replace_next = False
            append_body = False
            new_text = "\n\t"
            char = ''
            last_char = ''
            body = []
            count = 1
            num_dots = 0

            for k in range(len(words)):

                if k > 0 and char != "":
                    last_char = char

                char = words[k]
                if char == " " and last_char == " ":
                    replace_next = False
                    char = ""

                if char in punctuation:
                    num_dots += 1
                    if num_dots == 5:
                        num_dots = 0
                        char += "\n\n    "
                        count = 4

                if count == line_length:
                    replace_next = True
                    count = 1

                if replace_next and char == " ":
                    char = "\n"
                    replace_next = False
                    append_body = True

                new_text += char

                if append_body:
                    body.append(new_text)
                    new_text = ""
                    append_body = False

                count += 1

            return body

        # Get the data from the web page
        data = asyncio.run(self.get_requests())
        soups = [bs(page.text, "html.parser") for page in data]

        # Filter only the text within <p> and <h> tags
        tags = [soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']) for soup in soups]
        body = [make_neat([tag.get_text() for tag in subtag]) for subtag in tags]
        text = ["".join(page) for page in body]

        return text

    async def get_requests(self):
        """Asynchronous function for getting html data from multiple sites at once."""
        async with httpx.AsyncClient() as client:
            reqs = [client.get(url) for url in self.pages]
            results = await asyncio.gather(*reqs)
            return results

    @staticmethod
    def url_type_error():
        """Raises an error if the WebScrape object is initialized with unsupported data types or structures"""
        raise TypeError("Expected list of strings, or single string as url parameter.")

    @staticmethod
    def parse_html(html):
        """Returns header and paragraph tags separated into 2 lists"""
        soup = bs(html, 'html.parser')
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        paragraphs = soup.find_all('p')
        return headers, paragraphs

    @staticmethod
    def google_search(query: str, domain_type='com', num_results=10):
        """Gets URL's from google to be scraped."""
        return [site for site in search(query, tld=domain_type, stop=num_results)]


def main():
    """Demo of how this module may be used"""
    ws = WebScraper("https://www.thepioneerwoman.com/food-cooking/recipes/a86328/how-to-make-hot-sauce/")
    ws.set_pages(ws.google_search("Hot wing recipes"))
    words = ws.get_txt()
    for i in words:
        print(i)


if __name__ == "__main__":
    main()

