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

def scrape_vnexpress_categories(max_pages=3, articles_per_page=5):
    """Enhanced VnExpress scraper that tries different category pages for variety"""
    print(f"🚀 Starting enhanced VnExpress scraping from different sections...")
    
    # Different VnExpress sections/categories to get variety
    categories = [
        ("Trang chủ", "https://vnexpress.net/"),
        ("Thời sự", "https://vnexpress.net/thoi-su"),
        ("Kinh doanh", "https://vnexpress.net/kinh-doanh"),
        ("Thể thao", "https://vnexpress.net/the-thao"),
        ("Giải trí", "https://vnexpress.net/giai-tri"),
        ("Sức khỏe", "https://vnexpress.net/suc-khoe"),
        ("Đời sống", "https://vnexpress.net/gia-dinh"),
        ("Du lịch", "https://vnexpress.net/du-lich"),
        ("Khoa học", "https://vnexpress.net/khoa-hoc"),
        ("Số hóa", "https://vnexpress.net/so-hoa")
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_articles_data = []
    
    # Use different categories as "pages" to get variety
    for page_num in range(1, min(max_pages + 1, len(categories) + 1)):
        try:
            category_name, url = categories[page_num - 1]
            
            print(f"\n📄 Scraping page {page_num} - {category_name}: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find article titles and links with multiple selectors
            title_elements = []
            
            # Try different selectors for different page layouts
            selectors = [
                "h3.title-news",
                "h2.title-news", 
                "h3.title_news",
                "h2.title_news",
                ".item-news h3",
                ".item-news h2",
                ".title-news",
                "article h3",
                "article h2"
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    title_elements = elements
                    print(f"✅ Found articles using selector: {selector}")
                    break
            
            print(f"📰 Found {len(title_elements)} articles on {category_name}")
            
            if not title_elements:
                print(f"❌ No articles found on {category_name}, skipping...")
                continue
            
            # Process articles from this category
            page_articles = []
            for i, title_element in enumerate(title_elements[:articles_per_page]):
                try:
                    # Extract title
                    title = clean_text(title_element.get_text())
                    
                    # Extract link
                    link_element = title_element.find('a') or title_element.find_parent('a')
                    if not link_element:
                        # Try to find link in parent elements
                        parent = title_element.parent
                        while parent and not link_element:
                            link_element = parent.find('a')
                            parent = parent.parent
                    
                    if link_element and link_element.get('href'):
                        article_url = link_element.get('href')
                        
                        # Make sure it's a full URL
                        if article_url.startswith('/'):
                            article_url = urljoin("https://vnexpress.net", article_url)
                        
                        print(f"📖 Processing {category_name}, article {i+1}: {title[:50]}...")
                        
                        # Extract article content
                        content = extract_article_content(article_url)
                        
                        # Generate summary
                        summary = simple_summarize(content)
                        
                        article_data = {
                            'page': page_num,
                            'category': category_name,
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
                    else:
                        print(f"⚠️ No link found for article: {title[:50]}...")
                    
                except Exception as e:
                    print(f"❌ Error processing {category_name}, article {i+1}: {e}")
                    continue
            
            print(f"✅ Completed {category_name}: {len(page_articles)} articles processed")
            
            # Add delay between categories
            if page_num < max_pages:
                print("⏳ Waiting before next category...")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error scraping {category_name}: {e}")
            continue
    
    # Create DataFrame and save to CSV
    if all_articles_data:
        df = pd.DataFrame(all_articles_data)
        
        # Save to CSV
        csv_filename = f"vnexpress_articles_categories_{max_pages}pages.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"\n🎉 Successfully saved {len(all_articles_data)} articles from {max_pages} categories to {csv_filename}")
        print(f"📊 Columns: {list(df.columns)}")
        print(f"📈 Average content length: {df['content_length'].mean():.0f} characters")
        print(f"📄 Articles per category breakdown:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"   {category}: {count} articles")
        
        # Display first few rows
        print("\n📋 Sample data:")
        print(df[['category', 'title', 'summary']].head(5).to_string(index=False))
        
        return df
    else:
        print("❌ No articles were successfully processed from any category")
        return None

if __name__ == "__main__":
    # Configuration
    MAX_CATEGORIES = 5  # Number of different categories to scrape
    ARTICLES_PER_CATEGORY = 3  # Number of articles per category to process
    
    print("🔧 Configuration:")
    print(f"   📄 Categories to scrape: {MAX_CATEGORIES}")
    print(f"   📰 Articles per category: {ARTICLES_PER_CATEGORY}")
    print(f"   📊 Total expected articles: ~{MAX_CATEGORIES * ARTICLES_PER_CATEGORY}")
    
    # Run the enhanced multi-category scraper
    df = scrape_vnexpress_categories(max_pages=MAX_CATEGORIES, articles_per_page=ARTICLES_PER_CATEGORY)
    
    if df is not None:
        filename = f"vnexpress_articles_categories_{MAX_CATEGORIES}pages.csv"
        print(f"\n🎉 Multi-category scraping completed! Check '{filename}' for results.")
    else:
        print("\n😞 Scraping failed. Please check the error messages above.")
