# coding:utf-8

'''
Arctime 账户自动签到
作者：雪山凌狐
日期：2020-05-11
版本号：1.0
网址：http://www.xueshanlinghu.com

Arctime 账户每天签到可以获得 20 积分（1 元 = 100 积分，即每日可以得 0.2 元。可以用于购买增值服务等），我们来写个自动化脚本吧！
'''

import requests
import sys
import logging
import datetime

init_login_url = "http://m.arctime.cn/home/user/login.html"
login_url = "http://m.arctime.cn/home/user/login_save.html"
ucenter_url = "http://m.arctime.cn/home/ucenter/index.html"
sign_url = "http://m.arctime.cn/home/ucenter/attendance.html"

def init_login():
    headers = {
        'Host': 'm.arctime.cn',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'http://m.arctime.cn/home/ucenter/index.html'
    }
    res = requests.get(init_login_url, headers=headers)
    if res.status_code == 200:
        res.encoding = 'utf-8'
        log_print("获取 cookies 成功")
        log_print(res.cookies)
        return res.cookies
    else:
        return None

def login():
    headers = {
        'Host': 'm.arctime.cn',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'http://m.arctime.cn/home/user/login.html'
    }
    body = "username=%s&password=%s&login_type=2" % (username, password)
    res = requests.post(login_url, data=body, headers=headers, cookies=cookies)
    if res.status_code == 200:
        res.encoding = "utf-8"
        content = res.json()
        if content.get("msg") == "登录成功":
            log_print("登录成功！")
            return True
        else:
            return False

def getmidstring(html, start_str, end):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()

def auto_sign():
    headers = {
        'Host': 'm.arctime.cn',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'http://m.arctime.cn/home/user/login.html'
    }
    res = requests.get(ucenter_url, headers=headers, cookies=cookies)
    if res.status_code == 200:
        res.encoding = 'utf-8'
        content = res.text
        # 获取现有积分
        points = getmidstring(content, "共获得", "积分")
        log_print("您目前拥有的积分为：%s" % points)
        if content.find("立即签到领取积分") > -1:
            headers = {
                'Host': 'm.arctime.cn',
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0',
                'Referer': 'http://m.arctime.cn/home/ucenter/index.html'
            }
            body = " "
            res = requests.post(sign_url, data=body, headers=headers, cookies=cookies)
            if res.status_code == 200:
                res.encoding = "utf-8"
                content = res.json()
                log_print(content.get("msg"))
        elif content.find("今日已经签到") > -1:
            log_print("您今天已经签到过了")
        else:
            log_print("未知报错，请检查程序或联系作者！")
    else:
        log_print("访问用户个人中心页面失败")

# 在容器里运行时时间为 UTC 时间，不是北京时间，需要进行调整
def beijing(sec, what):
    beijing_time = datetime.datetime.now() + datetime.timedelta(hours=8)
    return beijing_time.timetuple()

def log_setting():
    """配置日志设置"""
    LOG_FILE_NAME = "log.log"
    LOG_PATH = LOG_FILE_NAME
    log_level = logging.INFO
    # 在容器里运行时时间为 UTC 时间，不是北京时间，需要进行调整
    logging.Formatter.converter = beijing
    logging.basicConfig(level=log_level,
                        format='[%(asctime)s] - [line:%(lineno)d] - %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=LOG_PATH,
                        filemode='a')
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    return logger

def log_print(msg, level="info", to_log_file=True, to_console=True):
    """
    日志输出封装功能
    :param msg: 要输出的信息
    :param level: 日志级别，一般有 debug, info, warning, error, critical 等
    :param to_log_file: 是否保存到日志文件中
    :param to_console: 是否在控制台输出
    """
    if to_log_file:
        if level == 'debug':
            logger.debug(msg)
        elif level == 'info':
            logger.info(msg)
        elif level == 'warning':
            logger.warning(msg)
        elif level == 'error':
            logger.error(msg)
        elif level == 'critical':
            logger.critical(msg)
    if to_console:
        print(msg)

   
if __name__ == '__main__':
    # 日志配置
    logger = log_setting()

    if len(sys.argv) != 3:
        raise Exception("传入参数不正确，第一个传入参数为登入的账号，第二个传入账户为密码")

    username = sys.argv[1]
    password = sys.argv[2]

    # 初始化登录，获取 cookies
    cookies = init_login()
    if cookies:
        # 登录
        res = login()
        if res:
            # 检测并自动签到
            auto_sign()
        else:
            log_print("登录失败！")
    else:
        log_print("初始化失败！")
