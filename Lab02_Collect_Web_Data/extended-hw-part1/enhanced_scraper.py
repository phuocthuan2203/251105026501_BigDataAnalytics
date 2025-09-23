import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin, urlparse

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def extract_article_content(url):
    """Extract the main content from a VnExpress article"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # VnExpress article content is typically in these selectors
        content_selectors = [
            '.fck_detail',
            '.Normal',
            'article .content',
            '.content_detail'
        ]
        
        content = ""
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Get all paragraph text
                paragraphs = content_div.find_all(['p', 'div'])
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                break
        
        return clean_text(content)
    
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return ""

def simple_summarize(text, max_sentences=3):
    """Simple extractive summarization - takes first few sentences"""
    if not text:
        return ""
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Take first few sentences as summary
    summary_sentences = sentences[:max_sentences]
    summary = '. '.join(summary_sentences)
    
    # Limit length
    if len(summary) > 300:
        summary = summary[:297] + "..."
    
    return summary

def scrape_vnexpress_enhanced(max_pages=3, articles_per_page=10):
    """Enhanced VnExpress scraper with multi-page support, links, content, and summaries"""
    print(f"🚀 Starting enhanced VnExpress scraping for {max_pages} pages...")
    
    base_url = "https://vnexpress.net"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_articles_data = []
    
    for page_num in range(1, max_pages + 1):
        try:
            # Construct URL for each page
            if page_num == 1:
                url = base_url
            else:
                url = f"{base_url}?page={page_num}"
            
            print(f"\n📄 Scraping page {page_num}: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find article titles and links
            title_elements = soup.find_all("h3", class_="title-news")
            
            if not title_elements:
                print(f"⚠️ No articles found on page {page_num}, trying alternative selectors...")
                # Try alternative selectors for different page layouts
                title_elements = soup.find_all("h3", class_="title_news") or soup.find_all("h2", class_="title-news")
            
            print(f"📰 Found {len(title_elements)} articles on page {page_num}")
            
            if not title_elements:
                print(f"❌ No articles found on page {page_num}, skipping...")
                continue
            
            # Process articles from this page
            page_articles = []
            for i, title_element in enumerate(title_elements[:articles_per_page]):
                try:
                    # Extract title
                    title = clean_text(title_element.get_text())
                    
                    # Extract link
                    link_element = title_element.find('a')
                    if link_element and link_element.get('href'):
                        article_url = link_element.get('href')
                        
                        # Make sure it's a full URL
                        if article_url.startswith('/'):
                            article_url = urljoin(url, article_url)
                        
                        print(f"📖 Processing page {page_num}, article {i+1}: {title[:50]}...")
                        
                        # Extract article content
                        content = extract_article_content(article_url)
                        
                        # Generate summary
                        summary = simple_summarize(content)
                        
                        article_data = {
                            'page': page_num,
                            'title': title,
                            'link': article_url,
                            'content_preview': content[:200] + "..." if len(content) > 200 else content,
                            'summary': summary,
                            'content_length': len(content),
                            'scraped_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        page_articles.append(article_data)
                        all_articles_data.append(article_data)
                        
                        # Be respectful to the server
                        time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Error processing page {page_num}, article {i+1}: {e}")
                    continue
            
            print(f"✅ Completed page {page_num}: {len(page_articles)} articles processed")
            
            # Add delay between pages
            if page_num < max_pages:
                print("⏳ Waiting before next page...")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error scraping page {page_num}: {e}")
            continue
    
    # Create DataFrame and save to CSV
    if all_articles_data:
        df = pd.DataFrame(all_articles_data)
        
        # Save to CSV
        csv_filename = f"vnexpress_articles_multipage_{max_pages}pages.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"\n🎉 Successfully saved {len(all_articles_data)} articles from {max_pages} pages to {csv_filename}")
        print(f"📊 Columns: {list(df.columns)}")
        print(f"📈 Average content length: {df['content_length'].mean():.0f} characters")
        print(f"📄 Articles per page breakdown:")
        page_counts = df['page'].value_counts().sort_index()
        for page, count in page_counts.items():
            print(f"   Page {page}: {count} articles")
        
        # Display first few rows
        print("\n📋 Sample data:")
        print(df[['page', 'title', 'summary']].head(5).to_string(index=False))
        
        return df
    else:
        print("❌ No articles were successfully processed from any page")
        return None

if __name__ == "__main__":
    # Configuration
    MAX_PAGES = 3  # Number of pages to scrape
    ARTICLES_PER_PAGE = 5  # Number of articles per page to process
    
    print("🔧 Configuration:")
    print(f"   📄 Pages to scrape: {MAX_PAGES}")
    print(f"   📰 Articles per page: {ARTICLES_PER_PAGE}")
    print(f"   📊 Total expected articles: ~{MAX_PAGES * ARTICLES_PER_PAGE}")
    
    # Run the enhanced multi-page scraper
    df = scrape_vnexpress_enhanced(max_pages=MAX_PAGES, articles_per_page=ARTICLES_PER_PAGE)
    
    if df is not None:
        filename = f"vnexpress_articles_multipage_{MAX_PAGES}pages.csv"
        print(f"\n🎉 Multi-page scraping completed! Check '{filename}' for results.")
    else:
        print("\n😞 Scraping failed. Please check the error messages above.")
