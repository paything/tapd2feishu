import os
import io
import json
import requests
from requests.auth import HTTPBasicAuth
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # 添加这行导入
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from docx import Document
from docx.shared import Inches
from PIL import Image

def tapd_login(headless=False):
      chrome_options = Options()
      if headless:
              chrome_options.add_argument('--headless')
              chrome_options.add_argument('--no-sandbox')
              chrome_options.add_argument('--disable-dev-shm-usage')
       
      chrome_driver_path = '/Users/chromedriver-mac-arm64/chromedriver'  # 更新为实际路径
      driver_service = Service(executable_path=chrome_driver_path)
      driver = webdriver.Chrome(service=driver_service, options=chrome_options)

      # driver.get('https://doc.google.com/')
      # driver.execute_script("document.getElementById('identifierId').value='xxxx@mail.com';")
      # driver.execute_script("document.getElementById('identifierNext').click();")
      # time.sleep(5) #给点时间登陆谷歌账号，如果要爬谷歌的图片需要用到
      # driver.execute_script("document.getElementsByName('Passwd')[0].value='password123';")
      # driver.execute_script("document.getElementById('passwordNext').click();")
      # time.sleep(15) #给点时间登陆谷歌账号，如果要爬谷歌的图片需要用到

      driver.get('https://www.tapd.cn/cloud_logins/login')

      
      driver.execute_script("document.getElementById('username').value='133333333333';")
      driver.execute_script("document.getElementById('password_input').value='psw1234567';")
      driver.execute_script("document.getElementById('protocol-checkbox').click();")
      driver.execute_script("document.getElementById('tcloud_login_button').click();")
       
      time.sleep(2)
      if '登录' in driver.title:
              raise Exception('登录失败，请检查用户名和密码')
       
      return driver


def get_all_stories():
      all_stories = []
      page = 1
      while True:
              print(page)
              url = 'https://api.tapd.cn/stories'
              params = {
                      'workspace_id': workspace_id,
                      'page': page,
                      'limit': '200',
                      'order': 'created desc',
                      'fields': 'id',
                      # 'name' :'6月爱的浪潮'
              }
               
              response = requests.get(url, params=params, auth=HTTPBasicAuth(username, password))
              response_json = response.json()
               
              if 'data' in response_json and response_json['data']:
                      all_stories.extend(response_json['data'])
                      page += 1
                      time.sleep(1)  # 防止tapd频控          
              else:
                      break

      return all_stories

def download_images(driver, all_stories):
    cnt = 0
    

    for story_entry in all_stories:
        cnt += 1
        print(f'第{cnt}个页面')
        
        # print(story_entry['Story'])
        story_id = story_entry['Story']['id']
        story_short_id = story_entry['Story']['id'][-7:]
        link = f'https://www.tapd.cn/{workspace_id}/prong/stories/view/{story_id}'
        
        # 打开指定的 URL
        driver.get(link)
        print(link)

        # 给页面加载时间
        time.sleep(2)
        
        driver.execute_script("document.write(document.getElementById('description_div').innerHTML,document.getElementById('comment_area').innerHTML);")
        driver.execute_script("document.querySelectorAll('table').forEach(table => {table.style.border = '1px solid black';table.style.borderCollapse = 'collapse';table.querySelectorAll('td, th').forEach(cell => {cell.style.border = '1px solid black';});});")
        target_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))        
        # 检查 target_div 内容是否为空
        if not target_div.text.strip():
            print(f'空内容 {story_short_id}, 不截图了.')
            continue

        # 获取页面总高度
        total_height = driver.execute_script('return document.body.scrollHeight')
        # 获取浏览器的视窗高度
        viewport_height = driver.execute_script('return window.innerHeight')

        # 初始化滚动位置和拼接的图片对象
        scroll_position = 0
        screenshots = []

        # 截取页面截图并滚动
        while True:
              # 截图
              screenshot = driver.get_screenshot_as_png()
              screenshots.append(Image.open(io.BytesIO(screenshot)))

              # 滚动页面
              scroll_position += viewport_height
                
              # 判断是否滚动到底部
              if scroll_position >= total_height:
                      break

              driver.execute_script(f'window.scrollTo(0, {scroll_position});')
               
              # 等待滚动完成，便于减少截图误差
              time.sleep(1)
               
              # 更新总高度，考虑动态加载的高度变化
              new_total_height = driver.execute_script('return document.body.scrollHeight')
              if new_total_height > total_height:
                      total_height = new_total_height

        # 创建综合的空白图像
        total_image = Image.new('RGB', (screenshots[0].width, total_height))

        # 粘贴截图到综合图像
        cur_height = 0
        for i in range(len(screenshots)):
              if cur_height + viewport_height > total_height:
                      # 最后一块截图的起始位置
                      crop_height = total_height - cur_height
                      box = (0, viewport_height - crop_height, screenshots[i].width, viewport_height)
                      total_image.paste(screenshots[i].crop(box), (0, cur_height))
              else:
                      total_image.paste(screenshots[i], (0, cur_height))
              cur_height += viewport_height

        # 保存最终的拼接图像
        story_dir = os.path.join(base_dir, story_short_id)
        os.makedirs(story_dir, exist_ok=True)
        total_image.save(os.path.join(story_dir, 'screenshot.png'))
        print('截图完成')
        print(os.path.join(story_dir, 'screenshot.png'))
    

# TAPD的APi账号密码
username = 'DDDDDDDD'
password = 'EEEEEEEE-CDB1-4BD6-A881-AAAAAAAAAAA'
# TAPD要迁移的项目ID
# ['技术中心']='111111111'
# ['本地化组']='222222222'
# ['美宣']='444444444'


# 请选择你的项目
workspace_id = '555555555'
base_dir = '/Users/Downloads/tapd_transmit_data_description_comment_shot/'+workspace_id



driver = tapd_login()
all_stories = get_all_stories()
print(all_stories)
download_images(driver,all_stories)