import logging

from playwright.async_api import Page


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
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Optional: Print scroll progress
        print(f"Completed scroll {i + 1}/{n}")

        # Wait for content to load
        await page.wait_for_timeout(delay_ms)


class ActionsService:
    def __init__(self):
        pass

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

    async def search_and_scroll(self, page: Page, search_term: str, should_like_tweets: bool):

        try:

            search_input_selector = '''//input[@placeholder='Search']'''
            await page.locator(search_input_selector).fill(search_term)
            await page.wait_for_timeout(2.3 * 1000)
            await page.keyboard.press(key='Enter')
            await page.wait_for_timeout(2.4 * 1000)

            await scroll_n_times(page, 10, delay_ms=4.5 * 1000)

            tweet_article_selector = '''//article[@data-testid="tweet"]'''
            tweets = await page.locator(tweet_article_selector).all()

            for tweet in tweets:
                await tweet.focus()
                await page.wait_for_timeout(3.1 * 1000)

                if should_like_tweets:
                    like_button_selector = ''''//button[contains(@aria-label, "Like")]'''
                    await tweet.locator(like_button_selector).click()

        except Exception as e:
            logging.error(f'Error in viewing tweets for search term = {search_term}', exc_info=e)
