import logging

from playwright.async_api import Page


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
