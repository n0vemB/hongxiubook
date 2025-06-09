import os
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm
import logging
from urllib.parse import urljoin
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_chapter_content_parallel(chapter_url, delay):
    """
    用selenium获取章节页面正文内容 (独立函数，用于并发下载)
    每次调用都会创建并关闭自己的WebDriver实例
    """
    driver = None # Initialize driver to None
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # Suppress ChromeDriver log output to avoid clutter
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(chapter_url)
        time.sleep(delay)  # Use the scraper's delay

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        content_div = soup.select_one('div.read-content')
        if not content_div:
            logger.error(f"未找到正文内容: {chapter_url}")
            return chapter_url, None

        paragraphs = content_div.find_all('p')
        content_lines = []
        for p in paragraphs:
            for span_tag in p.find_all('span'):
                span_tag.decompose()
            text = p.get_text(strip=True)
            if text:
                content_lines.append(text)
        content = '\n'.join(content_lines)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return chapter_url, content
    except Exception as e:
        logger.error(f"获取章节内容出错 {chapter_url}: {str(e)}")
        return chapter_url, None
    finally: # Ensure driver is quit regardless of success or failure
        if driver:
            driver.quit()

class HongxiuScraper:
    def __init__(self, delay=2):
        """
        初始化红袖添香小说爬虫
        
        Args:
            delay (int): 请求间隔时间(秒)
        """
        self.base_url = "https://www.hongxiu.com"
        self.delay = delay
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Referer': 'https://www.hongxiu.com/',
            'Connection': 'keep-alive',
        })
        # 初始化selenium driver (只用于 get_novel_info 和 get_chapter_list)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # Suppress ChromeDriver log output to avoid clutter
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.driver = webdriver.Chrome(options=chrome_options)

    def get_page(self, url):
        """获取页面内容,包含错误处理和重试逻辑"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.error(f"获取页面失败 {url}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(self.delay * (attempt + 1))
        return None

    def get_novel_info(self, novel_book_url):
        """
        用selenium获取小说信息，包括标题和作者
        """
        try:
            self.driver.get(novel_book_url)
            # Wait for the title element to be present
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.book-title'))
                )
                print("小说标题元素已找到，页面已渲染。")
            except Exception as e:
                print(f"等待小说标题元素超时或出错: {e}")
                print("可能小说主页结构已更改或加载问题。")
                # Continue even if not found, to capture page_source for debugging
            
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            title_tag = soup.select_one('h1.book-title')
            author_tag = soup.select_one('p.info-list span.book-author')

            # Debugging: Print found tags and relevant HTML
            # print("--- 小说信息调试开始 ---")
            # if title_tag:
            #     print(f"找到标题标签: {title_tag.prettify()[:200]}...")
            # else:
            #     print("未找到标题标签 (h1.book-info-title)。")
            
            # if author_tag:
            #     print(f"找到作者标签: {author_tag.prettify()[:200]}...")
            # else:
            #     print("未找到作者标签 (p.book-info-author a)。")

            # # Print a snippet of the page source where these elements are expected
            # # Look for a common parent like div.book-info
            # book_info_div = soup.select_one('div.book-info')
            # if book_info_div:
            #     print("--- book-info div HTML 片段 ---")
            #     print(str(book_info_div.prettify())[:1000]) # Print first 1000 chars
            #     print("--- book-info div HTML 片段结束 ---")
            # else:
            #     print("--- 未找到 div.book-info 元素，打印 body 内容 ---")
            #     body_tag = soup.find('body')
            #     if body_tag:
            #         print(str(body_tag.prettify())[:1000])
            #     else:
            #         print("未找到 body 标签。")
            #     print("--- body 内容结束 ---")
            # print("--- 小说信息调试结束 ---")

            title = title_tag.get_text(strip=True) if title_tag else "未知小说标题"
            author = author_tag.get_text(strip=True) if author_tag else "未知作者"

            return {'title': title, 'author': author}
        except Exception as e:
            logger.error(f"获取小说信息出错 {novel_book_url}: {str(e)}")
            return {'title': "未知小说标题", 'author': "未知作者"}

    def get_chapter_list(self, novel_url):
        """用selenium从章节列表页面解析所有章节链接和标题"""
        try:
            novel_id = novel_url.split('/')[-1]
            chapterlist_url = f"https://www.hongxiu.com/chapterlist/{novel_id}"
            self.driver.get(chapterlist_url)

            # Wait for the chapter list to be present
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.volume'))
                )
                print("章节列表元素已找到，页面已渲染。")
            except Exception as e:
                print(f"等待章节列表元素超时或出错: {e}")
                print("可能页面未完全加载或CSS选择器不正确。")
                # Fallback to a longer sleep if waiting fails, to give it more time for debugging purposes
                # time.sleep(5) # Removed this line as it's not needed with correct selector

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Find the specific div.volume that contains the actual chapter list
            chapter_list_volume_div = None
            all_volume_divs = soup.find_all('div', class_='volume')
            for vol_div in all_volume_divs:
                h3_tag = vol_div.find('h3')
                # Check if h3_tag exists and its text contains "正文卷"
                if h3_tag and '正文卷' in h3_tag.get_text():
                    chapter_list_volume_div = vol_div
                    break

            if not chapter_list_volume_div:
                logger.error("未找到包含'正文卷'的章节列表区域!")
                print("--- 未找到包含'正文卷'的章节列表区域，打印 body 内容 ---")
                body_tag = soup.find('body')
                if body_tag:
                    print(str(body_tag.prettify())[:5000])
                else:
                    print("未找到 body 标签。")
                print("--- body 内容结束 ---")
                return []

            # Debugging: Print relevant HTML section (kept for now, can be removed later)
            print("--- 章节列表 HTML 片段 (已过滤) ---")
            print(str(chapter_list_volume_div.prettify())[:5000]) # Print first 5000 chars for brevity
            print("--- 章节列表 HTML 片段结束 ---")

            chapter_links = chapter_list_volume_div.select('ul.cf li a')
            print(f"章节数: {len(chapter_links)}")
            for a in chapter_links[:5]:
                print(a.get('href'), a.get_text(strip=True))
            chapters = []
            for link in chapter_links:
                chapter_url = self.base_url + link['href']
                chapter_title = link.get_text(strip=True)
                chapters.append({
                    'url': chapter_url,
                    'title': chapter_title
                })
            return chapters
        except Exception as e:
            logger.error(f"解析章节列表页面出错: {str(e)}")
            return []

    def download_novel(self, novel_url, output_file, novel_info):
        """下载整本小说并保存到文件 (支持并发下载章节)"""
        try:
            chapters = self.get_chapter_list(novel_url)
            if not chapters:
                logger.error("未找到章节!")
                # Ensure the scraper's own driver is quit if no chapters found
                self.driver.quit()
                return False
            
            logger.info(f"找到 {len(chapters)} 个章节，开始并发下载...")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Prepare arguments for parallel processing
            chapter_urls_for_parallel = [chapter['url'] for chapter in chapters]
            
            # Map chapter_url to its title for ordered writing later
            chapter_url_to_title_map = {chapter['url']: chapter['title'] for chapter in chapters}

            # Use ThreadPoolExecutor for concurrent downloading
            # MAX_WORKERS controls how many Chrome instances run concurrently
            MAX_WORKERS = 10 
            
            # Store results by chapter URL to maintain order
            downloaded_contents = {} # {chapter_url: content}

            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Submit tasks and track their progress
                future_to_url = {executor.submit(get_chapter_content_parallel, url, self.delay): url 
                                 for url in chapter_urls_for_parallel}

                for future in tqdm(concurrent.futures.as_completed(future_to_url), 
                                   total=len(future_to_url), 
                                   desc="正在下载章节"):
                    chapter_url_completed = future_to_url[future]
                    try:
                        _, content = future.result() # get_chapter_content_parallel returns (url, content)
                        downloaded_contents[chapter_url_completed] = content
                    except Exception as exc:
                        logger.error(f'章节 {chapter_url_completed} 下载生成了一个异常: {exc}')
                        downloaded_contents[chapter_url_completed] = None # Mark as failed

            # Write all downloaded contents to file in original chapter order
            with open(output_file, 'w', encoding='utf-8-sig') as f:
                f.write(f"《{novel_info['title']}》\n")
                f.write(f"作者: {novel_info['author']}\n\n")
                f.write("="*50 + "\n\n")
                
                for chapter_obj in chapters: # Iterate through original ordered list
                    chapter_url = chapter_obj['url']
                    chapter_title = chapter_obj['title']
                    content = downloaded_contents.get(chapter_url)

                    if content:
                        f.write(f"\n\n{chapter_title}\n\n")
                        f.write(content)
                        f.write("\n" + "="*50 + "\n")
                    else:
                        logger.warning(f"跳过章节 {chapter_title} ({chapter_url})，因为它没有内容或下载失败。")
            
            logger.info(f"小说下载完成,保存至: {output_file}")
            # Ensure the scraper's own driver (used for get_novel_info and get_chapter_list) is quit
            self.driver.quit()
            return True
        except Exception as e:
            logger.error(f"下载小说时出错: {str(e)}")
            # Ensure the scraper's own driver is quit if an error occurs
            self.driver.quit()
            return False

def main():
    scraper = HongxiuScraper()

    novel_book_url = input("请输入小说主页地址 (例如: https://www.hongxiu.com/book/20912433708070004): ")
    
    novel_info = scraper.get_novel_info(novel_book_url)
    novel_title = novel_info['title']
    novel_author = novel_info['author']

    # Clean title for filename (remove invalid characters)
    invalid_chars = r'[<>:"/\\|?*]'
    novel_title_cleaned = re.sub(invalid_chars, '_', novel_title) # Replace invalid chars with underscore

    # Dynamically generate output file name
    output_file = f"novels/{novel_title_cleaned}.txt"

    scraper.download_novel(novel_book_url, output_file, novel_info)

if __name__ == "__main__":
    main() 