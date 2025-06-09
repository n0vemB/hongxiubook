# 红袖添香小说下载器

这是一个用于从红袖添香网站下载小说的 Python 脚本。它使用 Selenium 自动化浏览器来获取动态加载的章节列表和正文内容，并将整本小说保存为单个文本文件。

## 特性

-   自动获取小说章节列表。
-   下载小说正文内容。
-   自动识别并过滤网页中嵌入的干扰文字（如反爬虫字符）。
-   **支持手动输入小说主页地址。**
-   **自动抓取小说标题和作者。**
-   **根据小说标题动态生成输出文件名。**

## 环境配置

在运行脚本之前，请确保你的系统已安装以下依赖：

1.  **Python 3**
2.  **pip** (Python 包管理器)
3.  **Chrome 浏览器** (用于 Selenium 自动化)
4.  **ChromeDriver** (与你的 Chrome 浏览器版本相匹配)

### 安装 Python 依赖

在终端中运行以下命令来安装必要的 Python 库：

```bash
python3 -m pip install selenium beautifulsoup4 requests fake-useragent tqdm
```

### 安装 ChromeDriver（MAC系统）

1.  访问 [ChromeDriver 官方下载页面]
   https://chromedriver.chromium.org/downloads
   https://googlechromelabs.github.io/chrome-for-testing/。
2.  下载与你当前 Chrome 浏览器版本**完全匹配**的 ChromeDriver。
    -   要查看你的 Chrome 浏览器版本：在 Chrome 地址栏输入 `chrome://version`。
3.  解压下载的压缩包。你会看到一个名为 `chromedriver` 的可执行文件。
4.  将 `chromedriver` 文件移动到一个系统 PATH 目录中，例如 `/usr/local/bin`。

    ```bash
    # 假设你已进入解压后的 ChromeDriver 目录
    sudo mv chromedriver /usr/local/bin/
    ```
    （如果 `/usr/local/bin` 不存在，可以先用 `sudo mkdir -p /usr/local/bin` 创建。）

### 安装 ChromeDriver（windows系统）

   在 Windows 上设置 ChromeDriver，通常有两种方法：
   1、将 chromedriver.exe 放到系统 PATH 目录中： 这是最推荐的方法，因为这样你就可以在任何位置运行脚本而不需要指定 ChromeDriver 的完整路径。
   2、下载 chromedriver.exe 文件。
   3、将 chromedriver.exe 文件移动到你的 Windows 系统 PATH 环境变量中的任何一个目录里。
      常见的做法是放在：
      C:\Windows (系统目录，需要管理员权限)
      C:\Windows\System32 (系统目录，需要管理员权限)
      或者你自己创建的一个目录，然后将这个目录添加到系统 PATH 环境变量中（例如 C:\selenium_drivers）。
   4、如何添加目录到 PATH 环境变量（以 Windows 10/11 为例）：
      - 在 Windows 搜索栏输入“环境变量”，然后选择“编辑系统环境变量”。
      - 在“系统属性”窗口中，点击“环境变量”按钮。
      - 在“系统变量”部分，找到名为 Path 的变量，然后点击“编辑”。
      - 在“编辑环境变量”窗口中，点击“新建”，然后输入你存放 chromedriver.exe 的目录的完整路径（例如 C:\selenium_drivers）。
      - 点击“确定”关闭所有窗口。
      - 重要： 完成上述步骤后，关闭所有已打开的命令提示符或 PowerShell 窗口，然后重新打开一个新窗口，这样 PATH 环境变量的更改才会生效。


## 如何使用

1.  **运行脚本：**
    在终端中导航到 `novel_scraper.py` 文件所在的目录，然后运行：

    ```bash
    python3 novel_scraper.py
    ```

2.  **输入小说地址：**
    脚本会提示你输入要下载的小说主页地址。请确保输入的是**小说的主页 URL**，例如：

    ```
    请输入小说章节页地址 (例如: https://www.hongxiu.com/chapterlist/20912433708070004):
    ```
    将小说的 URL 粘贴到终端中，然后按回车键。

3.  **等待下载完成：**
    脚本将自动开始下载章节。下载进度将显示在终端中。下载完成后，小说会保存到 `novels/` 目录下，文件名为小说标题（例如 `novels/《你的小说标题》.txt`）。

## 注意事项

-   **网络连接：** 请确保你在运行脚本时有稳定的网络连接。
-   **反爬虫：** 如果网站的反爬虫机制更新，脚本可能需要根据网站结构的变化进行调整。
-   **日志：** 脚本会输出日志信息到终端，方便跟踪下载过程和调试潜在问题。

## Important Notes

1. **Legal and Ethical Considerations**:
   - Only download novels that you have the right to access
   - Respect the website's terms of service
   - Use this tool responsibly and for personal use only
   - Do not redistribute downloaded content

2. **Rate Limiting**:
   - The script includes a delay between requests to avoid overwhelming the server
   - Default delay is 2 seconds between requests
   - You can modify the delay in the code if needed

3. **Website Structure**:
   - The current selectors in the code are placeholders
   - You may need to modify the CSS selectors in `get_chapter_list()` and `get_chapter_content()` based on the specific website structure
   - Different websites may require different scraping approaches

## Customization

To adapt the scraper for a different website:

1. Modify the CSS selectors in `get_chapter_list()` and `get_chapter_content()`
2. Adjust the base URL in the `main()` function
3. Update the headers in `__init__()` if needed
4. Modify the delay time if required

## Error Handling

The script includes:
- Automatic retries for failed requests
- Logging of errors and progress
- Graceful handling of network issues
- File system error handling

## License

This project is for educational purposes only. Use responsibly and in accordance with applicable laws and website terms of service. 
