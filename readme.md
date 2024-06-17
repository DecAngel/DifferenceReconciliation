# 政府会计本年盈余与预算结余差异调节表自动化编制研究
## 安装
1. 安装python3.9，建立虚拟环境（推荐）
    ```shell
    virtualenv venv
    # linux
    source venv/bin/activate
    # windows
    .\venv\Scripts\activate
    ```
2. 安装Django
    ```shell
    python -m pip install django
    ```

## 运行
1. 启动http服务器
    ```shell
    python manage.py runserver localhost:8000 
    ```
2. 打开[http://127.0.0.1:8000/](http://127.0.0.1:8000/)浏览差异调节表结果
3. 打开[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)，输入用户名test，密码test，调整数据库内容（如微调会计凭证差异）
