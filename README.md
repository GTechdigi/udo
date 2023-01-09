# Udo 数据监控

Udo 数据监控是一款对数据同步,数据生成,数据预测做出监控的软件

## 功能支持

 - 域帐号/非域帐号登录
 - 添加数据源
    - 支持mysql, es, hive, clickhouse数据源
 - 对数据源数据做监控
    - 及时性监控: 预测数据记录数
        - 比如: 我们预测每日订单数不少于10000单, 少于10000单就报警
    - 数据同步监控: 监控数据同步任务是否成功执行
        - 比如: mysql同步数据到es, 可以监控每天mysql产生的数据记录数量于es中新增的数据记录数量相同
    - 一致性监控: 监控数据是否一致
        - 比如: mysql订单表同步数据到es后, 可以监控mysql新增的订单总GMV和es中新增的订单总GMV是否相同 
    - 业务监控: 根据指定的查询导出业务数据,并发送邮件或企业微信通知
        - 比如: 每小时查询一次创建失败的订单, 导出并发送邮件或企业微信通知
 - 定时执行监控任务
 - 支持监控报警:
    - 支持企业微信群聊机器人报警, 支持邮件报警(邮件发送使用了公司自己的邮件服务, 并不开源, 所以发送邮件步骤需要开发者自己实现)
 - 用户管理
 - 项目管理
 - 权限: 用户可以被添加到多个项目中, 基于项目创建规则和定时任务, 用户只能看到自己所在项目的规则和定时任务,只有管理员才可以看到所有,管理员可以在配置文件`default_setting.py`中配置`ADMIN = usernames`实现,多个用户名用逗号隔开

## 项目构成

前后端分类, [有度·UDO前端](https://github.com/GTechdigi/udo-web)采用vue，后端采用python3.9 + flask + APScheduler + sqlalchemy + [Apollo](https://github.com/apolloconfig/apollo) + redis + mysql

apollo客户端引用了[apollo-client-python](https://github.com/xhrg-product/apollo-client-python) , 并做了小幅修改,配置文件`default_setting.py`从`Aollo`中读取配置,所有配置都可设置默认值,所以`Apollo`非必需. 

## 准备事项：

- 如果是windows系统，在pip install的时候会报错，requirements.txt中去掉两行

   ```
   krbcontext==0.10
   kerberos==1.3.1
   ```
   因为有hive kerberos相关依赖在windows环境无法安装。
   install成功之后， 会有编译报错，需要修改`udo/utils/Connection.py` 文件
   ```
   __hive函数下面if语句块要注释掉， 同时因为注释掉if语句块， 而无用的import也要注释掉
   
       if default_settings.HAVE_KERBEROS:
   ```

- 配置`default_setting.py`

   ```
   REDIS_URL # redis地址
   SQLALCHEMY_DATABASE_URI #mysql地址
   SCHEDULER_JOBSTORES_URL #mysql地址 可与SQLALCHEMY_DATABASE_URI相同
   OSS_*  # oss相关配置
   LDAP_*  # 域帐号相关配置
   HAVE_KERBEROS # false 监控的hive没有开启kerberos认证
   KERBEROS_DOMAIN # kerberos认证的principal 例如：hive/a@b.com
   ```

- 如果监控的hive开启了kerberos认证， 需要在`udo/resource`目录添加对应的`.keytab`文件和`.conf`文件
如下：
  
   ```
   udo
     - resource
       - DEV-hive.keytab
       - DEV-krb5.conf
   ```
   文件名中的`DEV`是`default_setting.py`中的 `env_str = client.get_value("ENV", default_val="DEV")`， 主要用于多环境配置


## 开始使用

执行mysql初始化脚本：`udo/reource/sql/init.sql`
初始帐号 `admin/123456`

```
pip install -r requirements.txt
python run_server.py
```

