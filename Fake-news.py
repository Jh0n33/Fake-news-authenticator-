import tkinter as tk
from tkinter import messagebox
import requests

# ---- Constants ---- #
NEWS_API_KEY = "555c23279695426594eb9c0815f45fd5"
NEWS_API_URL = "https://newsapi.org/v2/everything"
HUGGINGFACE_API_TOKEN = ""
SENTIMENT_API_URL = "https://api-inference.huggingface.co/models/nlptown/bert-base-multilingual-uncased-sentiment"

# ---- Classes ---- #
class NewsFetcher:
    """
     A class for fetching news articles from the News API.

     Attributes:
         api_key (str): The API key for the News API.
     """

    def __init__(self, api_key):
        """
             Initializes the NewsFetcher object with the API key.

             Args:
                 api_key (str): The API key for the News API.
        """
        self.api_key = api_key

    def get_headlines(self, keyword):
        """
        Fetches news headlines based on the given keyword.

        Args:
            keyword (str): the keyword to search for in the news headlines.

        Returns:
           list: a list of news headlines.

        Raises:
            Exception: if the API request fails or returns an error.
        """
        url = f"{NEWS_API_URL}?q={keyword}&apiKey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            return [article['title'] for article in articles]
        else:
            raise Exception("Failed to fetch news. Check API key or internet connection.")


class FakeNewsDetector:
    """
    A class for detecting fake news using the Hugging Face API.
    """
    def __init__(self, token):
        """
        Initializes the FakeNewsDetector object with the API token.

        Args:
            token (str): The API token for the Hugging Face API.
        """
        self.api_url = SENTIMENT_API_URL  # Store the API URL
        self.headers = {  # Construct the headers for the API request
        "Authorization": f"Bearer {token}",  # Include the API token in the headers
        "Content-Type": "application/json"  # Specify the content type as JSON
    }

    def check_news(self, text):
        """
        Checks the given news text for sentiment and determines if it's fake or real.

        Args:
            text (str): The news text to check.

        Returns:
            str: A verdict on whether the news is fake or real.

        Raises:
            Exception: If the API request fails or returns an error.
        """
        payload = {"inputs": text}  # Construct the payload for the API request
        response = requests.post(self.api_url, headers=self.headers, json=payload)  # Make a post-request to the API

        # DEBUG: Print the actual result
        print("Fake News API response:", response.text)
        if response.status_code == 200:  # Check if the response is successful
            result = response.json()  # Get the JSON response
            # Handle a nested list from Hugging Face
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                top_prediction = result[0][0]  # Get the highest scoring prediction
                label = top_prediction["label"]  # Get the label of the prediction
                stars = int(label[0])  # Extract the number of stars from the label
                if stars <= 2:  # Determine the verdict based on the number of stars
                    return f"Possibly FAKE ({label})"
                elif stars == 3:
                    return f"Uncertain ({label})"
                else:
                    return f"Likely REAL ({label})"
            # Model not ready or error

            # Class for detecting fake news (continued)
            # Model not ready or error
            elif isinstance(result, dict) and "error" in result:
                return f"Model not ready: {result['error']}"
            else:
                return "Unexpected response format."
        else:
            raise Exception(f"Fake news detection failed. Status code: {response.status_code}")


# ---- GUI Class ---- #
class NewsApp:
    """
    A class for the GUI application.
    """
    def __init__(self, root):
        """
        Initializes the NewsApp object with the root window.

        Args:
            root (tk.Tk): The root window of the GUI application.
        """
        self.root = root
        self.root.title("Fake News Detector")
        self.fetcher = NewsFetcher(NEWS_API_KEY)
        self.detector = FakeNewsDetector(HUGGINGFACE_API_TOKEN)
        self.setup_gui()

    def setup_gui(self):
        """
        Sets up the GUI components.
        """
        tk.Label(self.root, text="Enter Keyword:").pack()
        self.keyword_entry = tk.Entry(self.root, width=50)
        self.keyword_entry.pack()

        tk.Button(self.root, text="Fetch News", command=self.fetch_news).pack(pady=5)
        self.news_listbox = tk.Listbox(self.root, width=80, height=15)
        self.news_listbox.pack()

        tk.Button(self.root, text="Check news authenticity", command=self.check_selected_news).pack(pady=5)

    def fetch_news(self):
        """
        Fetches news articles based on the keyword entered by the user.
        """
        keyword = self.keyword_entry.get()
        if not keyword.strip():
            messagebox.showinfo("Info", "Please enter a keyword.")
            return
        try:
            headlines = self.fetcher.get_headlines(keyword)
            self.news_listbox.delete(0, tk.END)
            if not headlines:
                self.news_listbox.insert(tk.END, "No news found for that keyword.")
            else:
                for headline in headlines:
                    self.news_listbox.insert(tk.END, headline)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def check_selected_news(self):
        """
        Checks the selected news article for fake news.
        """
        try:
            selected_index = self.news_listbox.curselection()
            if not selected_index:
                messagebox.showinfo("Info", "Please select a news headline first.")
                return
            selected_news = self.news_listbox.get(selected_index)
            verdict = self.detector.check_news(selected_news)
            messagebox.showinfo("Fake News Verdict", f"Result: {verdict}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---- Main ---- #
if __name__ == "__main__":
    root = tk.Tk()
    app = NewsApp(root)
    root.mainloop()
  
