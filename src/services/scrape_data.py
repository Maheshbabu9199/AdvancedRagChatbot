from playwright.async_api import async_playwright, Page, Browser
from src.utilities.constants import ConstantsFetcher
from src.utilities.logger import Logger
from typing import List, Dict, Any
import json
import asyncio
import os

logger = Logger.getLogger(__name__)


class ScrapeData:

    def finalize_chunk(self, current_content: str, current_h1: str, current_h2: str, current_h3: str, current_h4: str, title: str, url: str, depth: int, documents: List[Dict[str, Any]]):
        if current_content.strip():
            # Use h1 as heading if available, otherwise use page title
            heading = current_h1 if current_h1 else title
            
            # Build subheading from the hierarchy of headings available
            subheading_parts = [h for h in [current_h2, current_h3, current_h4] if h]
            if not current_h1 and current_h2: # If no h1, h2 is not part of subheading
                subheading_parts.pop(0)
                                    
            subheading_text = " : ".join(subheading_parts) if subheading_parts else ""
            
            documents.append({
                "url": url,
                "depth": depth,
                "title": title,
                "heading": heading,
                "subheading": subheading_text,
                "content": current_content.strip()
            })


    async def parse_wikipedia_page(self, page: Page, url: str, depth: int = 1) -> List[Dict[str, Any]]:
        """
        Parse Wikipedia page and extract structured chunks with h1/h2/h3/h4 and metadata.
        """
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_selector("#mw-content-text .mw-parser-output", timeout=25000, state="attached")
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
        except Exception:
            logger.exception(f"Failed to load or process page {url}")
            return []

        title = await page.title()

        # Define the selector for all content tags we are interested in
        content_selector = ", ".join([f"#mw-content-text .mw-parser-output {tag}" for tag in ["h1", "h2", "h3", "h4", "p", "li"]])

        # Extract only meaningful content tags
        elements = await page.eval_on_selector_all(
            content_selector,
            """
            els => els.map(el => {
                const text = (el.innerText || el.textContent || "").trim();
                // Exclude certain known-bad text from Wikipedia articles
                if (text === "Contents" || text.startsWith("This article needs additional citations for verification.")) return null;
                return {
                    tag: el.tagName.toLowerCase(),
                    text: text
                };
            }).filter(e => e.text.length > 0)
            """
        )
        
        documents = []
        current_h1 = None
        current_h2 = None
        current_h3 = None
        current_h4 = None
        current_content = ""


        for el in elements:
            tag = el["tag"]
            text = el["text"]

            if tag in ["h1", "h2", "h3"]:
                self.finalize_chunk(current_content, current_h1, current_h2, current_h3, current_h4, title, url, depth, documents)
                current_content = "" # Reset content for new section
                if tag == "h1":
                    current_h1 = text
                    current_h2 = current_h3 = current_h4 = None
                elif tag == "h2":
                    current_h2 = text
                    current_h3 = current_h4 = None
                elif tag == "h3":
                    current_h3 = text
                    current_h4 = None
            elif tag == "h4":
                current_h4 = text
            else:
                current_content += text + " "

        self.finalize_chunk(current_content, current_h1, current_h2, current_h3, current_h4, title, url, depth, documents)
        return documents, title
    
    async def scrape_single_url(self, url: str, browser: Browser):
        """
        """
        page = await browser.new_page()
        logger.info(f"🔹 Scraping {url}")
        docs, title = await self.parse_wikipedia_page(page, url)
        logger.info(f"  → Found {len(docs)} chunks for {url}")
        await page.close()
        return docs, title


    async def scrape_wikipedia_pages(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        """
        results = []
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            tasks = [self.scrape_single_url(url, browser) for url in urls]
            pages_results = await asyncio.gather(*tasks)
            
            all_docs = []
            for docs, title in pages_results:
                all_docs.extend(docs)

                # Sanitize title to create a valid filename
                safe_filename = "".join([c for c in title if c.isalpha() or c.isdigit() or c in (' ', '-')]).rstrip()
                json_filename = f"{safe_filename}.json"
                
                # Storing in the json file
                folder_path = ConstantsFetcher.fetch_constants('documents')['folderpath']
                with open(os.path.join(folder_path, json_filename), "w", encoding="utf-8") as f:
                    json.dump(docs, f, ensure_ascii=False, indent=4)
                logger.info(f"  → Saved {len(docs)} chunks to {json_filename}")

            await browser.close()
        return all_docs


# Example usage
if __name__ == "__main__":
    urls_to_scrape = [
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Computer"]

    scrapper = ScrapeData()

    scraped_docs = asyncio.run(scrapper.scrape_wikipedia_pages(urls_to_scrape))
    logger.info(f"\nTotal documents scraped: {len(scraped_docs)}\n")

    