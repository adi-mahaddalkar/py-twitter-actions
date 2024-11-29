import asyncio
import json
import logging
import os
import uuid
from typing import Optional, List, Set
import pandas as pd

from playwright.async_api import Page, async_playwright

logging.basicConfig(level=logging.DEBUG)

PROXY_SETTINGS = {
    "server": "http://brd.superproxy.io:22225",
    "username": "brd-customer-hl_c5cadfc7-zone-isp",  # Optional
    "password": "ozsaiwh340kv"  # Optional
}

HEADLESS = False
VIDEO_FOLDER = 'temp'
DATA_FOLDER = 'run-8-final'
SCROLL = 5


async def scroll_n_times(page: Page, n: int, delay_ms: int | float = 1000) -> None:
    """
    Scrolls the page by document length n times with a configurable delay between scrolls.

    Args:
        page: Playwright page object
        n: Number of times to scroll
        delay_ms: Delay between scrolls in milliseconds (default: 1000ms)
    """
    for i in range(n):
        # Scroll by one viewport height
        await page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")

        # Optional: Print scroll progress
        logging.debug(f"Completed scroll {i + 1}/{n}")

        # Wait for content to load
        await page.wait_for_timeout(delay_ms)


class ActionsService:
    def __init__(self):
        os.makedirs(DATA_FOLDER, exist_ok=True)

    async def login(self,
                    page: Page,
                    username: str,
                    password: str):
        try:
            await page.goto('https://x.com/i/flow/login')

            email_input_selector = '''//input[@name='text']'''
            next_button_selector = '''//button//*[contains(text(), 'Next')]'''
            await page.locator(email_input_selector).fill(username)
            await page.wait_for_timeout(2.3 * 1000)
            await page.locator(next_button_selector).click()
            await page.wait_for_timeout(2.5 * 1000)

            password_selector = '''//input[@name='password']'''
            login_button_selector = '''//button//*[contains(text(), 'Log in')]'''
            await page.locator(password_selector).fill(password)
            await page.wait_for_timeout(2.6 * 1000)
            await page.locator(login_button_selector).click()
            await page.wait_for_timeout(1.7 * 1000)
        except Exception as e:
            logging.error(f'Error in logging in for user = {username} and password = {password}', exc_info=e)

    async def scroll_through_home_page(self, page: Page, links_output_filename: str | os.PathLike,
                                       is_before: bool = True):

        try:
            await page.goto('https://x.com')
            await page.wait_for_timeout(2.5 * 1000)

            fyp_tweet_links = set()

            tweets_set = set()
            tweet_article_selector = '''//article[@data-testid="tweet"]'''

            for scroll in range(SCROLL):

                tweets = await page.locator(tweet_article_selector).all()

                for tweet in tweets:
                    tweet_id = await tweet.get_attribute('aria-labelledby')
                    tweets_set.add((tweet_id, tweet))

                for idx, (_, tweet) in enumerate(tweets_set):
                    try:
                        await tweet.focus()
                        await page.wait_for_timeout(3.1 * 1000)
                        is_before_string = 'before' if is_before else 'after'
                        await page.screenshot(path=os.path.join(DATA_FOLDER, f'fyp-{is_before_string}-{scroll}-{idx}.png'))
                    except Exception as e:
                        logging.error(f'Error while saving tweet screenshot on FYP', exc_info=e)

                tweets_set = set()

                tweet_links = await self.extract_tweet_links(page=page)

                if tweet_links is not None and len(tweet_links) > 0:
                    fyp_tweet_links.update(tweet_links)

                await scroll_n_times(page=page, n=1, delay_ms=3.7 * 1000)

            if len(fyp_tweet_links) > 0:
                df = pd.DataFrame({
                    'links': list(fyp_tweet_links)
                })

                df.to_csv(os.path.join(DATA_FOLDER, links_output_filename))

        except Exception as e:
            logging.error(f'Error in scrolling through home page', exc_info=e)

    async def search_and_scroll(self, page: Page, search_term: str, should_like_tweets: bool):

        try:

            await page.goto('https://x.com')
            await page.wait_for_timeout(3.5 * 1000)

            search_input_selector = '''//input[@placeholder='Search']'''
            await page.locator(search_input_selector).fill(search_term)
            await page.wait_for_timeout(2.3 * 1000)
            await page.keyboard.press(key='Enter')
            await page.wait_for_timeout(2.4 * 1000)

            tweets_set = set()
            tweet_article_selector = '''//article[@data-testid="tweet"]'''

            for scroll in range(SCROLL):
                tweets = await page.locator(tweet_article_selector).all()

                for tweet in tweets:
                    tweet_id = await tweet.get_attribute('aria-labelledby')
                    tweets_set.add((tweet_id, tweet))

                await scroll_n_times(page, 1, delay_ms=4.5 * 1000)

            logging.info(f'Found {len(tweets_set)} tweets for search query = {search_term}')

            for _, tweet in tweets_set:
                await tweet.focus()
                await page.wait_for_timeout(3.1 * 1000)

                if should_like_tweets:
                    like_button_selector = ''''//button[contains(@aria-label, "Like")]'''
                    await tweet.locator(like_button_selector).click()

        except Exception as e:
            logging.error(f'Error in viewing tweets for search term = {search_term}', exc_info=e)

    async def tweet_action(self, page: Page, tweet_url: str, should_like: bool, should_retweet: bool, idx: int):

        try:

            logging.info(f'Trying tweet actions for tweet = {tweet_url}')

            await page.goto(tweet_url, wait_until='domcontentloaded')
            await page.wait_for_timeout(6.7 * 1000)

            if should_like:
                await page.locator('''//button[@data-testid="like"]''').first.click()
                await page.wait_for_timeout(6.3 * 1000)

            if should_retweet:
                await page.locator('''//button[@data-testid="retweet"]''').first.click()
                await page.wait_for_timeout(3.1 * 1000)

                await page.locator('''//span[contains(text(), 'Repost')]''').click()
                await page.wait_for_timeout(5.5 * 1000)

            await page.screenshot(path=os.path.join(DATA_FOLDER, f'tweet-{idx}.png'))

        except Exception as e:
            logging.error(f'Error while performing actions on tweet = {tweet_url}', exc_info=e)

    async def extract_tweet_links(self, page: Page) -> Optional[Set]:

        try:

            tweet_links = await page.locator(
                '''//article//a[contains(@href, '/status/') and not(contains(@href, 'analytics'))]''').all()
            await page.wait_for_timeout(2.4 * 1000)

            tweet_link_set = set()

            for link in tweet_links:
                url = await link.get_attribute('href')
                tweet_link_set.add(url)

            return tweet_link_set

        except Exception as e:
            logging.error(f'Error in extracting tweet links from page', exc_info=e)
            return None

    async def run(self, username: str, password: str, tweet_links: Optional[List[str]]):

        _id = uuid.uuid4().__str__()

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                proxy=PROXY_SETTINGS,
                headless=HEADLESS,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                record_video_dir=DATA_FOLDER,
                record_video_size={"width": 1920, "height": 1080}
            )

            if os.path.isfile(f'{username}.json'):
                with open(os.path.join(f'{username}.json'), 'r') as f:
                    cookies = json.load(f)
                    await context.add_cookies(cookies)
                page = await context.new_page()
            else:
                page = await context.new_page()
                await self.login(page=page, username=username, password=password)

            await self.scroll_through_home_page(page=page, links_output_filename=f'{_id}_before.csv', is_before=True)

            if tweet_links is not None:
                for idx, tweet_link in enumerate(tweet_links):
                    await self.tweet_action(
                        page=page,
                        tweet_url=tweet_link,
                        should_like=False,
                        should_retweet=True,
                        idx=idx
                    )
            else:
                await self.search_and_scroll(page=page, search_term='thanksgiving', should_like_tweets=False)

            await self.scroll_through_home_page(page=page, links_output_filename=f'{_id}_after.csv', is_before=False)


if __name__ == '__main__':
    loop = asyncio.ProactorEventLoop()

    tweets = [
        'https://x.com/l4dybugg__/status/1860939515503825219',
        'https://x.com/moesize/status/1858275294089797781',
        'https://x.com/hungrykittie/status/1860638148394447118',
        'https://x.com/IvanSuicideBoy/status/1859003161757028553',
        'https://x.com/sigmamummo/status/1859276985467289780',
        'https://x.com/Mika_trinaXO/status/1859907777831088470',
    ]

    loop.run_until_complete(ActionsService().run(
        username='IlyasSilva11341',
        password='Silva+Ilyas13',
        tweet_links=tweets
    ))
