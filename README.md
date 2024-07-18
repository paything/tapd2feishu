# tapd2feishu
从tapd的接口，拉取需求列表story

拿到需求ID+需求描述，将需求描述里面的html部份抽出来
提取img标签，拼上tapd的前缀，得到图片地址

再开启一个chrome浏览器，用js的方式读取图片再把图片保存下来，多个也存
最后保存到一个文件夹中

/需求id/image_序号.png


第三步，从tapd的官方接口拉取所有的附件列表，然后逐个附件id换取下载链接，再立刻下载到本地中
/需求id/附件1.xxxx

第四步，
将本地文件上传到飞书，换取file_token
根据需求id，找到飞书的record_id（需要手动先迁移文本数据）
然后再根据record_id+file_token去更新文档记录

注意修改main_directory来读取数据，文件夹里面需要是一个文件夹list，文件夹名称为【需求id】
