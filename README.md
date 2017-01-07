## 使用 mongodb python-eve 搭建类似 leancloud 的后端数据存储服务


## 系统环境

ubuntu 16.04 64 bit

安装一些基础包

```shell
apt-get update
apt-get upgrade -y
apt-get install -y sudo curl wget zip unzip vim virtualenv apache2-utils
```

## 安装 mongodb

参考 [https://docs.mongodb.com/manual/administration/install-on-linux/](https://docs.mongodb.com/manual/administration/install-on-linux/)


```shell
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org

systemctl start mongod
systemctl enable mongod
```

## 安装 python-eve

将 python-eve 安装在 `/opt/eve` 目录下

```shell
mkdir -p /opt/eve && cd /opt/eve
virtualenv -p python3 venv
source venv/bin/activate
pip install eve
deactivate
```

新建 `eve app`，也可以参考这里 [http://python-eve.org/quickstart.html](http://python-eve.org/quickstart.html)

```shell
cd /opt/eve

vi app.py
```

```python
from eve import Eve
from flask import current_app as app


test = {
    'allow_unknown': True,
    'resource_methods': ['GET', 'POST']
}

config = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'test',
    'URL_PREFIX': 'api',
    'API_VERSION': 'v1',
    'DEBUG': False,
    'DOMAIN': {'test': test}
}


app = Eve(settings=config)
app.run()
```

另附一份我启用了 `HMAC-SHA1` 鉴权的配置, 真实环境运行时可以参考使用 [/opt/eve](https://github.com/xdtianyu/CallerBackend/tree/master/opt/eve)


运行测试

```shell
/opt/eve/venv/bin/python app.py
```

出现如下内容说明运行成功


```
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

添加 `systemd` 服务

```shell
[Service]
ExecStart=/opt/eve/venv/bin/python /opt/eve/app.py
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=eve
User=nobody
Group=nogroup
#Environment=
[Install]
WantedBy=multi-user.target
```

启用 eve 服务


```
systemctl start eve
systemctl enable eve
```

可以使用 `journalctl -u eve` 命令查看服务状态


## 安装 adminMongo web 管理服务

安装 nodejs，参考 [https://nodejs.org/en/download/package-manager/](https://nodejs.org/en/download/package-manager/)

```shell
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs
```
安装 `adminMongo`, 参考 [https://github.com/mrvautin/adminMongo](https://github.com/mrvautin/adminMongo)

```shell
mkdir -p /opt/adminMongo && cd /opt/adminMongo
npm i admin-mongo
```

修改 `config/app.json` 配置文件内容为

```json
{
    "app": {
        "host": "127.0.0.1",
        "port": 18080,
        "password": "admin",
        "locale": "en",
        "context": "mongo",
        "monitoring": true
    }
}
```

启动 `adminMongo`

```shell
/usr/bin/node /opt/adminMongo/app.js
```

出现如下内容说明启动成功

```
adminMongo listening on host: http://127.0.0.1:18080/mongo
```

添加 `systemd` 服务

```
vi /etc/systemd/system/admin-mongo.service
```

```
[Service]
ExecStart=/usr/bin/node /opt/adminMongo/app.js
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=admin-mongo
User=nobody
Group=nogroup
Environment=NODE_ENV=production
[Install]
WantedBy=multi-user.target
```

启用服务

```
chown -R nobody:nogroup /opt/adminMongo
systemctl start admin-mongo
systemctl enable admin-mongo
```

可以使用 `journalctl -u admin-mongo` 命令查看服务状态


## 安装 mongo-express web 管理服务

参考 [https://github.com/mongo-express/mongo-express](https://github.com/mongo-express/mongo-express)

```shell
mkdir -p /opt/mongo-express && cd /opt/mongo-express
npm install mongo-express
```

修改配置文件

```
vi /opt/mongo-express/node_modules/mongo-express/config.default.js
```

查找并修改如下内容

```js
  mongo = {
    db: 'test',
    host:     'localhost',
    password: '',
    port:     27017,
    ssl:      false,
    url:      'mongodb://localhost:27017',
    username: '',
  };
```

```
    //baseUrl: process.env.ME_CONFIG_SITE_BASEURL || '/',
    baseUrl: '/express/',
```

```
  //useBasicAuth: process.env.ME_CONFIG_BASICAUTH_USERNAME !== '',
  useBasicAuth: false,

  basicAuth: {
    username: process.env.ME_CONFIG_BASICAUTH_USERNAME || '',
    password: process.env.ME_CONFIG_BASICAUTH_PASSWORD || '',
  },
```

启动 `mongo-express`

```
/usr/bin/node /opt/mongo-express/node_modules/mongo-express/app.js
```

出现如下内容说明启动成功

```
No custom config.js found, loading config.default.js
Welcome to mongo-express
------------------------


Mongo Express server listening at http://localhost:8081
Database connected
Connecting to test...
Database test connected
```

添加 `systemd` 服务

```
vi /etc/systemd/system/mongo-express.service
```

```
[Service]
ExecStart=/usr/bin/node /opt/mongo-express/node_modules/mongo-express/app.js
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=mongo-express
User=nobody
Group=nogroup
#Environment=
[Install]
WantedBy=multi-user.target
```

启动服务

```
chown -R nobody:nogroup /opt/mongo-express
systemctl start mongo-express
systemctl enable mongo-express
```

可以使用 `journalctl -u mongo-express` 命令查看服务状态

## 安装 nginx 并配置 https 和代理

```shell
apt install nginx-extras
```

添加配置

```
vi /etc/nginx/sites-available/backend
```

注意修改 `backend.example.org` 为你的域名，证书路径修改为你的路径

```
server {
    listen       80;
    listen       443 ssl http2;
    server_name  backend.example.org;
    
    ssl_certificate le/certs/backend.example.org/fullchain.pem;
    ssl_certificate_key le/certs/backend.example.org/privkey.pem;
    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    charset utf-8;
    access_log  /var/log/nginx/$host.access.log;
    client_max_body_size 20M;
    root   /var/www/;
    index  index.html index.htm;
    if ($ssl_protocol = "") {
        return 301 https://$http_host$request_uri;
    }
    location / {
        try_files $uri $uri/ =404;
    }
    location /express {
        auth_basic "Authentication required";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://localhost:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    #error_page  404              /404.html;
    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
    location /api/v1/ {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-NginX-Proxy true;
        proxy_pass http://localhost:5000/api/v1/;
        proxy_ssl_session_reuse off;
        proxy_set_header Host $http_host;
        proxy_redirect off;
    }
    location /mongo {
        auth_basic "Authentication required";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://localhost:18080/mongo;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```
cd /etc/nginx/sites-enabled/
ln -s ../sites-available/backend

```

创建 `.htpasswd` 文件，通过 `http basic auth` 保护 web 管理终端，因为配合了 `HTTPS` 使用，所以已经足够安全。

```
cd /etc/nginx/
htpasswd  -c .htpasswd YOUR_HTTP_USER
```

使用 `nginx -t` 测试，如果出现错误，请按照提示修改


启动 nginx 服务


```
systemctl start nginx
systemctl enable nginx
```

## 安装完成

可以在浏览器打开测试

`https://backend.example.org/api/v1` 是 `eve api` 路径

`https://backend.example.org/mongo` 是 `adminMongo` web 管理面板

`https://backend.example.org/express` 是 `mongo-express` web 管理面板


`eve api` 具有较高的定制性，灵活且方便使用，可以非常轻松的实现手机终端上报数据存储功能。浏览器打开时会使用 `xml` 格式展示，可以使用 [postman](https://www.getpostman.com/) 来调试接口。

另附一个我启用 `HMAC-SHA1` 鉴权后, Android 客户端 `okhttp hmac post` 的实现 

[phone-number/src/main/java/org/xdty/phone/number/net/cloud/CloudHandler.java#L95](https://github.com/xdtianyu/PhoneNumber/blob/0f95cda40940055cae284498dcaf99c29bee61a6/phone-number/src/main/java/org/xdty/phone/number/net/cloud/CloudHandler.java#L95)

**注意**

如果启用了 api 认证，例如 [app.py#L15](https://github.com/xdtianyu/CallerBackend/tree/master/opt/eve/app.py#L15) 请一定要在数据库中增加类似 `accounts` 这样的 `collection`，具体字段由你的配置决定。内容参考如下

```
{
    "userid": "6Yd5MtkpdSZcJrtEtk",
    "secret_key": "7dBvS2Ow3RSIr9gdAmLDCRD8EI1dbMecGTOJ"
}
```

更多关于 `python-eve` 的配置请阅读官方文档 [http://python-eve.org/quickstart.html](http://python-eve.org/quickstart.html)

安装完成后，整个系统内存仅使用 200m 左右，cpu 几乎无负载。
