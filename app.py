import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from transformers import BartTokenizer, BartForConditionalGeneration, BertTokenizer, BertForSequenceClassification
import torch
import pandas as pd

USER_AGENT = 'Scrapper/1.0 (sinhaaman650@gmail.com)'

app = Flask(__name__)
CORS(app)

# Load the summarization model
bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

# Load the categorization model
bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = BertForSequenceClassification.from_pretrained("bert-base-uncased")

def fetch_news(url):
    # Initialize Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('title').get_text(strip=True)
    content = ' '.join(p.get_text(strip=True) for p in soup.find_all('p'))
    date = soup.find('time').get('datetime') if soup.find('time') else 'No Date'
    link = url
    
    content_cleaned = re.sub(r'\s+', ' ', content)
    article = {'title': title, 'content': content_cleaned, 'date': date, 'source': link}
    
    return article

def summarize_text(text, max_length=150, min_length=30):
    inputs = bart_tokenizer.encode(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = bart_model.generate(inputs, max_length=max_length, min_length=min_length, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def categorize_text(text):
    inputs = bert_tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
    outputs = bert_model(**inputs)
    logits=outputs.logits
    # Get the predicted category 
    prediction = torch.argmax(logits, dim=1).item()
    # Map the prediction to a human-readable category 
    categories = ["Politics", "Technology", "Sports", "Entertainment", "Business"] 
    category = categories[prediction]
    return category

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    article = fetch_news(url)
    if isinstance(article, str):
        return jsonify({'error': article}), 400
    
    article_summary = summarize_text(article['content'])
    article['summary'] = article_summary
    article['category'] = categorize_text(article['content'])

    return jsonify(article)

if __name__ == '__main__':
    app.run(debug=True)
