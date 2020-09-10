from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import selenium.common.exceptions as ex
import time
from spotify.extendtions import db
from spotify.models import Link, Order
from dateutil.relativedelta import relativedelta
import datetime



def login(driver, email, password):
    try:
        driver.get('https://www.spotify.com/us/account/profile/')
        inputs = WebDriverWait(driver, 15, 0.5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'input'))
        )
        inputs[0].clear()
        inputs[0].send_keys(email)
        inputs[1].send_keys(password)
        log_in_btn = driver.find_element_by_id('login-button')
        log_in_btn.click()
        time.sleep(5)
        if driver.current_url=='https://www.spotify.com/us/account/profile/':
            return 'login success'
        else:
            msg=driver.find_element_by_xpath('/html/body/div/div[2]/div/div[2]/div/p/span').text
            return msg

    except Exception as e:
        return 'retry'

def change_profile(driver):
    try:
        usa = WebDriverWait(driver, 15, 0.5).until(
            EC.presence_of_element_located((By.ID,
                                            'country'))
        )
        Select(usa).select_by_value('US')
        driver.find_element_by_xpath(
            '/html/body/div[1]/div[4]/div/div[2]/div[2]/div[2]/div/article/section/form/div/button').click()
    except Exception as e:
        return 'retry'

def retry_change_profile(driver):
    driver.get('https://www.spotify.com/us/account/profile/')
    try:
        usa = WebDriverWait(driver, 15, 0.5).until(
            EC.presence_of_element_located((By.ID,
                                            'country'))
        )
        Select(usa).select_by_value('US')
        driver.find_element_by_xpath(
            '/html/body/div[1]/div[4]/div/div[2]/div[2]/div[2]/div/article/section/form/div/button').click()
        return 'change profile success'
    except Exception as e:
        return 'retry'



def confirm_address(driver, link):
    try:
        link_split = link.infos.split('/')
        token = link_split[-1]
        if len(token) < 1:
            token = link_split[-2]
        link_address = 'https://www.spotify.com/us/family/join/address/' + token + '/'
        driver.get(link_address)
        address_input = WebDriverWait(driver, 15, 0.5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/form/main/div/section/div/div[2]/input'))
        )
        address_input.send_keys('1')
        find_adress = driver.find_element_by_xpath('/html/body/div[2]/form/main/div/div/button')
        find_adress.click()
        confirm_btn = WebDriverWait(driver, 15, 0.5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/footer/button[2]'))
        )
        confirm_btn.click()
        time.sleep(5)

        if driver.current_url == 'https://www.spotify.com/us/family/join/confirmation/':
            return 'success'
        else:
            return 'retry'

    except Exception as e:

        if driver.current_url == 'https://www.spotify.com/us/account/family/':
            return 'already family'
        else:
            try:
                msg = WebDriverWait(driver, 30, 0.5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[2]/main/div/section/h1'))
                )
                return msg.text
            except Exception as e:
                return 'retry_not_change_link'


def get_link(order, driver):
    while True:
        link = Link.query.filter(Link.isvalid==True).first()
        if not link:
            order.status = '没有可用链接'
            db.session.commit()
            driver.close()
            driver.quit()
            return None
        if link.times > 0:
            break
        else:
            link.isvalid=False
            link.reason='达到使用次数上限'
            db.session.commit()
    return link


def get(email, password, link):
    option = webdriver.ChromeOptions()
    option.add_argument('--no-sandbox')
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')
    option.add_argument('--hide-scrollbars')
    option.add_argument('blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(chrome_options=option)
    driver.delete_all_cookies()
    order = Order(email=email, password=password, link=link)
    db.session.add(order)
    db.session.commit()

    # 处理登录问题
    retry_times = 6
    login_result = login(driver, email, password)
    while login_result != 'login success':
        retry_times -= 1
        login_result = login(driver, email, password)
        if retry_times == 0:
            # 更新账号或密码错误状态
            if login_result=='retry':
                order.status='网络中断，请稍后重试'
            elif 'Oops!' in login_result:
                order.status = 'vpn代理中断，请稍后重试'
            elif 'username' in login_result:
                order.status='账号或密码错误'
            db.session.commit()
            driver.close()
            driver.quit()
            return None

    # 修改账号地区
    retry_times = 6
    profile_result=change_profile(driver)
    while profile_result == 'retry':
        profile_result=retry_change_profile(driver)
        retry_times -= 1
        if retry_times == 0:
            order.status = '网络中断，请稍后重试'
            db.session.commit()
            driver.close()
            driver.quit()
            return None
    # 进入邀请链接
    retry_times = 6
    result = confirm_address(driver, link)
    while result != 'success':
        if result == 'already family':
            order.status = '已经是会员'
            db.session.commit()
            driver.close()
            driver.quit()
            return None
        # 一年内已经开通过一次
        elif result == 'You can’t join this plan':
            order.status = '12个月内只能开通一次'
            db.session.commit()
            driver.close()
            driver.quit()
            return None
        elif result=='retry_not_change_link':
            #    时间超时了
            retry_times -= 1
            result = confirm_address(driver,link)
            if retry_times == 0:
                order.status = '网络中断，请稍后重试'
                db.session.commit()
                driver.close()
                driver.quit()
                return None
        else:
            # 获取下个链接
            link.isvalid=False
            link.reason=result
            db.session.commit()
            link=get_link(order,driver)
            result = confirm_address(driver, link)
            retry_times -= 1
            if retry_times == 0:
                order.status = '网络中断，请稍后重试'
                db.session.commit()
                driver.close()
                driver.quit()
                return None

    order.status = '处理成功'
    link.times -= 1
    order.expiretime = datetime.datetime.utcnow() + relativedelta(years=1)
    db.session.commit()
    driver.close()
    driver.quit()
    return None
