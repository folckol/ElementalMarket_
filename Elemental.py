import datetime
import json
import os
import random
import ssl
import time
import traceback
from pathlib import Path
from typing import Generator

import cloudscraper
import pytest
import requests

from playwright.sync_api import sync_playwright, Playwright, BrowserContext, expect

collections = {'BSC': ['https://element.market/collections/metamergepet',
                       'https://element.market/collections/g3m-nft-series',
                       'https://element.market/collections/playbux-early-bird-quest'],
               'ZK': ['https://element.market/collections/zk_dagger',
                            'https://element.market/collections/zkapepunks-club',
                            'https://element.market/collections/zkhamsters',
                            'https://element.market/collections/zkunicorns'],
               'POLYGON': ['https://element.market/collections/league-of-kingdoms-polygon',
                            'https://element.market/collections/planet-ix-assets',
                            'https://element.market/collections/galaxy-oat2']}

def random_user_agent():
    browser_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Edge/{3}.{4}.{5}'
    ]

    chrome_version = random.randint(108, 114)
    firefox_version = random.randint(108, 114)
    safari_version = random.randint(605, 610)
    edge_version = random.randint(15, 99)

    chrome_build = random.randint(9000, 9999)
    firefox_build = random.randint(1, 100)
    safari_build = random.randint(1, 50)
    edge_build = random.randint(1000, 9999)

    browser_choice = random.choice(browser_list)
    user_agent = browser_choice.format(chrome_version, firefox_version, safari_version, edge_version, chrome_build, firefox_build, safari_build, edge_build)

    return user_agent

def acp_api_send_request(page, message_type, data={}):
    message = {
        # всегда указывается именно этот получатель API сообщения
        'receiver': 'antiCaptchaPlugin',
        # тип запроса, например setOptions
        'type': message_type,

        # мерджим с дополнительными данными
        **data
    }
    # выполняем JS код на странице
    # а именно отправляем сообщение стандартным методом window.postMessage

    page.evaluate("""
        window.postMessage({});
        """.format(json.dumps(message)))

    return True

@pytest.fixture()
def context(playwright: Playwright) -> Generator[BrowserContext, None, None]:
    path_to_extension = Path(__file__).parent.joinpath('10.32.0_0')
    print(path_to_extension)
    context = playwright.chromium.launch_persistent_context(
        "",
        headless=False,
        args=[
            f"--disable-extensions-except={path_to_extension}",
            f"--load-extension={path_to_extension}",
        ],
    )
    yield context
    context.close()

@pytest.fixture()
def extension_id(context) -> Generator[str, None, None]:
    # for manifest v2:
    # background = context.background_pages[0]
    # if not background:
    #     background = context.wait_for_event("backgroundpage")

    # for manifest v3:
    background = context.service_workers[0]
    if not background:
        background = context.wait_for_event("serviceworker")

    extension_id = background.url.split("/")[2]
    yield extension_id

class PWModel:

    def __init__(self, private, proxy):
        self.playwright = sync_playwright().start()

        self.privateKey,self.proxy = private, proxy

        EX_path = 'MetaMask'
        user_data_dir = f"{os.getcwd()}\\dataDir"


        self.context = self.playwright.chromium.launch_persistent_context(user_data_dir,
                                                                          user_agent=random_user_agent(),
                                                                     proxy={
            "server": f"{proxy.split(':')[0]}:{proxy.split(':')[1]}",
            "username": f"{proxy.split(':')[2]}",
            "password": f"{proxy.split(':')[3]}",
        },headless=False, devtools=False, args=[f'--load-extension={os.getcwd()}\\{EX_path}',
                                               f'--disable-extensions-except={os.getcwd()}\\{EX_path}'
                                               ])

        self.page = self.context.new_page()

        self.page.set_default_timeout(60000)




    def MMActivation(self):
        # Открытие страницы Twitter
        self.page.goto('https://twitter.com/home')
        self.page.wait_for_timeout(5000)

        # print(self.context.pages)

        self.MMPage = self.context.pages[-1]
        self.MMPage.wait_for_selector('input[id="onboarding__terms-checkbox"]').click()
        self.MMPage.wait_for_selector('button[data-testid="onboarding-create-wallet"]').click()
        self.MMPage.wait_for_selector('button[data-testid="metametrics-i-agree"]').click()
        self.MMPage.wait_for_selector('input[data-testid="create-password-new"]').fill('Passwordsdjeruf039fnreo')
        self.MMPage.wait_for_selector('input[data-testid="create-password-confirm"]').fill('Passwordsdjeruf039fnreo')
        self.MMPage.wait_for_selector('input[data-testid="create-password-terms"]').click()
        self.MMPage.wait_for_selector('button[data-testid="create-password-wallet"]').click()
        self.MMPage.wait_for_selector('button[data-testid="secure-wallet-later"]').click()
        self.MMPage.wait_for_selector('input[data-testid="skip-srp-backup-popover-checkbox"]').click()
        self.MMPage.wait_for_selector('button[data-testid="skip-srp-backup"]').click()
        self.MMPage.wait_for_selector('button[data-testid="onboarding-complete-done"]').click()
        self.MMPage.wait_for_selector('button[data-testid="pin-extension-next"]').click()
        self.MMPage.wait_for_timeout(1000)
        self.MMPage.wait_for_selector('button[data-testid="pin-extension-done"]').click()
        self.MMPage.wait_for_timeout(4000)
        self.MMPage.wait_for_selector('button[data-testid="popover-close"]').click()
        # self.MMPage.wait_for_timeout(1000)
        # self.MMPage.wait_for_selector('button[data-testid="popover-close"]').click()
        self.MMPage.wait_for_timeout(1000)
        self.MMPage.wait_for_selector('button[data-testid="account-menu-icon"]').click()
        self.MMPage.wait_for_selector('div.account-menu > button.account-menu__item.account-menu__item--clickable')
        self.MMPage.query_selector_all('div.account-menu > button.account-menu__item.account-menu__item--clickable')[1].click()
        self.MMPage.wait_for_selector('input[id="private-key-box"]').fill(self.privateKey)
        self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/button[2]').click()
        self.MMPage.wait_for_selector('button[data-testid="eth-overview-send"]')

    def InviteJoin(self):

        self.page.bring_to_front()
        self.page.goto('https://element.market/invite?ref=6X19')

        self.page.wait_for_selector('button.bind-invite-btn').click()

        pages_len = len(self.context.pages)
        self.page.wait_for_selector('xpath=//*[@id="root"]/div[1]/div/div/div/div[1]')
        self.page.wait_for_timeout(3000)
        self.page.wait_for_selector('xpath=//*[@id="root"]/div[1]/div/div/div/div[1]').click()
        while pages_len == len(self.context.pages):
            self.page.wait_for_timeout(1000)

        self.MMConfirmer = self.context.pages[-1]
        self.MMConfirmer.wait_for_selector('button.btn-primary').click()
        self.MMConfirmer.wait_for_selector('button[data-testid="page-container-footer-next"]').click()

        self.page.wait_for_timeout(10000)

        self.MMConfirmer = self.context.pages[-1]
        self.MMConfirmer.wait_for_selector('button[data-testid="page-container-footer-next"]').click()
        self.MMConfirmer.wait_for_timeout(2000)
        self.MMConfirmer.wait_for_selector('button[data-testid="page-container-footer-next"]').click()
        self.MMConfirmer.wait_for_timeout(2000)

        self.page.wait_for_selector('button.bind-invite-btn').click()
        self.page.wait_for_selector('button.invite-btn-two.rs-btn-primary').hover()
        self.page.wait_for_selector('button.invite-btn-two.rs-btn-primary').click()
        self.page.wait_for_selector('button.invite-btn-one').click()


    def TurnOnChain(self, network):

        if network == 'BSC':

            self.MMPage.wait_for_selector('div.network-display').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-secondary"]').click()
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div[4]/div[2]/button').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary"]').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary home__new-network-added__switch-to-button"]').click()
            self.MMPage.wait_for_timeout(5000)

        if network == 'POLYGON':
            self.MMPage.wait_for_selector('div.network-display').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-secondary"]').click()
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div[10]/div[2]/button').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary"]').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary home__new-network-added__switch-to-button"]').click()
            self.MMPage.wait_for_timeout(5000)

        if network == 'ZK':
            self.MMPage.wait_for_selector('div.network-display').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-secondary"]').click()
            self.MMPage.wait_for_selector('xpath=//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[3]/a/h6').click()

            self.MMPage.wait_for_selector('input.form-field__input')
            inputs = self.MMPage.query_selector_all('input.form-field__input')
            inputs[0].fill('zkSync Era Mainnet')
            inputs[1].fill('https://mainnet.era.zksync.io')
            inputs[2].fill('324')
            inputs[3].fill('ETH')
            inputs[4].fill('https://explorer.zksync.io/')

            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary"]').click()
            self.MMPage.wait_for_selector('button[class="button btn--rounded btn-primary home__new-network-added__switch-to-button"]').click()
            self.MMPage.wait_for_timeout(5000)

    def BuyNFT(self, chain):

        # self.page.wait_for_selector('div.layout-header-content-right.pc div.select-chain div.select-chain-on').click()
        # self.page.wait_for_selector('xpath=//*[@id="layout-header-popover"]/div[2]/div[2]')

        self.page.goto(random.choice(collections[chain]))
        self.page.wait_for_selector('div.element-asset-grid-item')

        self.page.query_selector_all('div.element-asset-grid-item')[1].hover()
        self.page.wait_for_timeout(2000)
        self.page.query_selector_all('div.element-asset-grid-item')[1].wait_for_selector('button.buy-now', state="visible").click()

        pages_len = len(self.context.pages)
        self.page.wait_for_selector('button[class="rs-btn rs-btn-primary rs-btn-lg"]').click()
        while pages_len == len(self.context.pages):
            self.page.wait_for_timeout(1000)

        self.MMConfirmer = self.context.pages[-1]
        self.MMConfirmer.wait_for_selector('button.btn-primary').click()
        # self.MMConfirmer.wait_for_selector('button[data-testid="page-container-footer-next"]').click()

        # self.page.wait_for_selector('div.accept-listing-popup-button button').click()
        self.page.wait_for_timeout(20000)


    def close(self):

        self.playwright.stop()

if __name__ == '__main__':

    start_time = time.time()
    try:

        network = 'BSC'

        Model = PWModel(private='', proxy="")
        Model.MMActivation()
        Model.InviteJoin()
        Model.TurnOnChain(network)
        Model.BuyNFT(network)
        Model.close()

        print('Готово')


    except:
        traceback.print_exc()


    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Время выполнения скрипта: {execution_time} секунд")
    Model.page.wait_for_timeout(10000000)

