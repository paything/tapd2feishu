import requests
from requests.auth import HTTPBasicAuth
import json
import time
import os

#寻找工单里面附件，有就加上
def get_all_attachments():
      all_attachments = []
      page = 6
      while True:
              print(page)
              # 获取每一页的数据
              url = 'https://api.tapd.cn/attachments/'
              params = {
                      'workspace_id': workspace_id,
                      'page': page,
                      'limit': '100',  # 可以根据需求调整这个值,最大200
                      # 'owner' :'张三',
                      # 'filename':'.png'
              }
               
              response = requests.get(url, params=params, auth=HTTPBasicAuth(username, password))
              response_json = json.loads(response.content.decode('utf-8'))

              # 检查是否返回数据
              if 'data' in response_json and response_json['data']:
                      all_attachments.extend(response_json['data'])
                      page += 1  # 获取下一页
                      time.sleep(1)  # 防止tapd频控   
              else:
                      break  # 没有更多的数据，跳出循环
      print(all_attachments)
      print(page)
      return all_attachments

def get_attachment_link(all_attachments):
      attachment_link=[]
      cnt=0
      if not os.path.exists(base_download_path):
         os.makedirs(base_download_path)
      for story_entry in all_attachments:
              cnt += 1
              print('附件链接请求，第N个附件',cnt)
              attachment_id = story_entry['Attachment']['id']
              url = 'https://api.tapd.cn/attachments/down'
              params = {
                      'workspace_id': workspace_id,
                      'id': attachment_id,
              }
               
              response = requests.get(url, params=params, auth=HTTPBasicAuth(username, password))
              response_json = response.json()
              if 'data' in response_json and response_json['data']['Attachment']:
                      data = response_json['data']['Attachment']
                      time.sleep(1)  # 防止tapd频控    
                      story_id = data['entry_id']
                      story_short_id = data['entry_id'][-7:]
                      filename = data['filename']
                      content_type = data['content_type']
                      owner = data['owner']
                      download_url = data['download_url']
                      print(story_short_id)
                      print(filename)
                      print(download_url)
                      # 构建文件夹和文件路径
                      story_folder_path = os.path.join(base_download_path, story_short_id)
                      if not os.path.exists(story_folder_path):
                          os.makedirs(story_folder_path)

                      file_path = os.path.join(story_folder_path, filename)

                      # 下载文件
                      try:
                          file_response = requests.get(download_url, auth=HTTPBasicAuth(username, password))

                          # 写文件
                          with open(file_path, 'wb') as file:
                              file.write(file_response.content)

                          time.sleep(1)  # 防止tapd频控   
                          
                          print(f'File {filename} downloaded and saved to {file_path}')
                      except Exception as e:
                          print(f'Failed to download or save file {filename}: {e}')      
              else:
                      break
      return attachment_link







# TAPD的APi账号密码
username = 'tapd的username'
password = 'EEEEEEEE-AAAA-4444-8888-EEEEEEEAAAA'
# TAPD要迁移的项目ID
# ['技术中心']='99999999'
# ['本地化']='555555555'
# 请选择你的项目
workspace_id = '44444444'


# 本地存储路径
base_download_path = '/Users/Downloads/tapd_transmit_data_attachment/'+workspace_id


# 获取全部附件
all_attachments = get_all_attachments()

# 通过附件id获取下载地址,顺便下载了
attachment_link = get_attachment_link(all_attachments)



