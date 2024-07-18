import os
import requests

# 飞书的API URL和认证Token
upload_url = 'https://open.feishu.cn/open-apis/drive/v1/medias/upload_all'
#可以在https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/list?appId=cli_a6666666666666生成
auth_token = 'u-asdfghjklzxcvbn12345678'  # 替换为实际的认证Token
#从飞书页面可以获取,替换为实际的内容
app_token = 'QkkLbB2FpaHC12345678567'
table_id = 'tblq0G0zxcvbn1234567456'
#记得写要更新哪个字段名/img_from_desc/attachment，替换为实际的内容
update_field_name='des_screen_shot'

# 主目录路径，需要上传附件的路径，替换为实际的内容
main_directory = '/Users/Downloads/tapd_transmit_data_attachment/55555555/'

# 构建记录API和基础更新URL
record_url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records'
base_update_url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records'




#上传本地文件，换取飞书file_token
def upload_file(file_path):
      file_name = os.path.basename(file_path)
      file_size = os.path.getsize(file_path)
      multipart_form_data = {
              'file_name': (None, file_name),  # 可以根据实际需要修改
              'parent_type': (None, 'bitable_file'),
              'parent_node': (None, app_token),  # 根据实际需要修改
              'size': (None, str(file_size)),
              'file': (file_name, open(file_path, 'rb'))
      }
      headers = {
              'Authorization': f'Bearer {auth_token}'
      }
      if file_size > 20 * 1024 * 1024:
        print(f'过大：File size for {file_path} is greater than 20MB, returning None.')
        return None
      response = requests.post(upload_url, headers=headers, files=multipart_form_data)
      
      if response.status_code == 200:
              print(response.json())
              return response.json().get('data', {}).get('file_token')
      else:
              print(f'Failed to upload {file_path}: {response.content}')
              return None


#根据多维表的id字段，拿到飞书的record_id
def get_record_id(data_id):
      # 您需要排除的 data_id 列表
      exclude_data_ids = {12345}
      
      if int(data_id) in exclude_data_ids: 
          # 如果 data_id 在排除列表里，直接返回 None
          print(f'排空：Data ID {data_id} is in the exclude list, returning None.')
          return None
      params = {
              'field_names': f'["ID", "{update_field_name}"]',
              'filter': f'AND(CurrentValue.[ID]="{data_id}")',
              'page_size': 20
      }
      headers = {
              'Authorization': f'Bearer {auth_token}'
      }
      response = requests.get(record_url, headers=headers, params=params)
      if response.status_code == 200:
              records = response.json().get('data', {}).get('items', [])
              print('去飞书看下记录ID')
              print(response.json())
              if records:
                      return records[0].get('record_id')
              else:
                      print(f'No record found for Data ID: {data_id}')
                      return None
      else:
              print(f'Failed to get record ID for {data_id}: {response.content}')
              return None

#飞书的record_id+file_token，去更新指定的字段
def update_data(record_id, filetokens):
      # 生成包含record_id的更新URL
      update_url = f'{base_update_url}/{record_id}'
      payload = {
              'fields': {
                      f'{update_field_name}': [{'file_token': filetoken} for filetoken in filetokens]
              }
      }
      headers = {
              'Authorization': f'Bearer {auth_token}',
              'Content-Type': 'application/json'
      }
      print(payload)
      response = requests.put(update_url, headers=headers, json=payload)
      if response.status_code == 200:
              print(f'Successfully updated data for record {record_id}')
      else:
              print(f'Failed to update data for record {record_id}: {response.content}')
# 主程序块
for folder_name in os.listdir(main_directory):
      folder_path = os.path.join(main_directory, folder_name)
      if os.path.isdir(folder_path) and folder_name.isdigit():
              data_id = folder_name
              record_id = get_record_id(data_id)
              if record_id:
                      filetokens = []  # 初始化用于存储filetoken的列表
                      for filename in os.listdir(folder_path):
                              file_path = os.path.join(folder_path, filename)
                              if os.path.isfile(file_path):
                                      filetoken = upload_file(file_path)
                                      if filetoken:
                                              filetokens.append(filetoken)
                      if filetokens:
                              update_data(record_id, filetokens)