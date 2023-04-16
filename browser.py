# coding=utf-8

# (credits) 作者：蒙舌上単 https://www.bilibili.com/read/cv20610733?from=articleDetail 出处：bilibili

import os
# import pytest
import time
import json
import datetime
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def log(str=""):
    print("[%s] %s" % (datetime.datetime.now(), str))


class ChatGPT(object):
    def __init__(self, port=None):
        options = Options()
        if port:
            options.add_experimental_option(
                "debuggerAddress", "127.0.0.1:%d" % port)

        self.driver = uc.Chrome(options=options)
        self.vars = {}
        self.reply_cnt = 0
        self.reply_cnt_old = 0

    def close(self):
        self.driver.quit()

    def open(self, delay=3, refresh=False):
        self.reply_cnt = 0
        self.reply_cnt_old = 0
        log("Opening ChatGPT...")
        
        self.driver.get("https://chat.openai.com")
        time.sleep(delay)
        log("Done")

    def send(self, str="你好", delay=0.25):
        self.reply_cnt_old = self.reply_cnt
        # click the textbox
        txtbox = self.driver.find_element(By.CSS_SELECTOR, ".m-0")
        txtbox.click()
        time.sleep(delay)
        # enter prompt
        log("Prompt:"+repr(str))
        txtlines = str.split('\n')
        for txt in txtlines:
            txtbox.send_keys(txt)
            time.sleep(delay)
            txtbox.send_keys(Keys.SHIFT, Keys.ENTER)
            time.sleep(delay)
        # send
        txtbox.send_keys(Keys.ENTER)
        time.sleep(delay)

    def regenerate(self):
        self.reply_cnt = self.reply_cnt_old
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
    
    def deleteChat(self):
        # click delete button
        time.sleep(1)
        self.driver.find_elements(By.XPATH, '//button[@class="p-1 hover:text-white"]')[1].click()
        time.sleep(0.5)

        # click check button
        self.driver.find_elements(By.XPATH, '//button[@class="p-1 hover:text-white"]')[0].click()
        time.sleep(1)

    def getLastReply(self, timeout=90):
        log("Waiting for reply...")
        time_cnt = 0
        reply_str = ""

        # wait for chatgpt responding
        while self.driver.find_elements(By.CSS_SELECTOR, ".result-streaming") != []:
            if time_cnt >= timeout:
                reply_str += "【Timeout: %d sec" % timeout
                elemList = self.getReplyList()
                if len(elemList) <= self.reply_cnt:
                    reply_str += ", no reply】"
                    return reply_str, False
                else:
                    reply_str += "】\n"
                    break

            time.sleep(1)
            time_cnt = time_cnt + 1

        elemList = self.getReplyList()
        if len(elemList) <= self.reply_cnt:
            return "【Error】", False

        for i in range(self.reply_cnt, len(elemList)):
            reply_str += elemList[i].text
            reply_str += "\n"

        log(reply_str)
        self.reply_cnt = len(elemList)
        return reply_str, True

    def getReplyList(self):
        return self.driver.find_elements(By.CSS_SELECTOR, ".markdown > p")


if __name__ == "__main__":
    chatgpt = ChatGPT()
    #chatgpt.init(9222)
    chatgpt.open()
    while True:
        str = input(
            "=====================\nPlease enter your prompt,\nrestart: Ctrl+Q, regenerate: Ctrl+R, exit: Ctrl+C\n>>> ")
        if str.find(chr(17)) > -1:
            chatgpt.open(refresh=True)
        elif str.find(chr(18)) > -1:
            chatgpt.regenerate()
        else:
            chatgpt.send(str=str)
        print(chatgpt.getLastReply()[0])
        chatgpt.deleteChat()

