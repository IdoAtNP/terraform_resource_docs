"""HTML fetcher for Terraform Registry pages."""

import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger


class PageFetcher:
    """Fetches JavaScript-rendered pages using Selenium."""
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 10,
        wait_time: int = 2
    ):
        """
        Initialize the page fetcher.
        
        Args:
            headless: Run browser in headless mode
            timeout: Maximum time to wait for page elements
            wait_time: Extra wait time after page load
        """
        self.headless = headless
        self.timeout = timeout
        self.wait_time = wait_time
        
    def _create_driver(self) -> webdriver.Chrome:
        """Create a configured Chrome WebDriver instance."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver
    
    def fetch(self, url: str) -> Optional[str]:
        """
        Fetch a JavaScript-rendered page.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None if fetch failed
        """
        logger.bind(url=url).info("Fetching page")
        driver = None
        
        try:
            driver = self._create_driver()
            driver.get(url)
            
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            time.sleep(self.wait_time)
            
            html = driver.page_source
            logger.bind(html_length=len(html)).debug("Page fetched successfully")
            
            return html
            
        except TimeoutException:
            logger.bind(url=url, timeout=self.timeout).error("Timeout waiting for page to load")
            return None
            
        except WebDriverException as e:
            logger.bind(url=url, error=str(e)).error("WebDriver error occurred")
            return None
            
        except Exception as e:
            logger.bind(url=url, error=str(e)).error("Unexpected error during fetch")
            return None
            
        finally:
            if driver:
                driver.quit()

