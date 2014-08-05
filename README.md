eduCloud
========

support both virtual desktop and virtual server, based on vbox, a simple eucalyptus re-implementation by python.


1.系统架构说明

Luhya私有云平台同时提供了虚拟服务器和虚拟桌面两种服务。它的系统架构说明如下：
- 系统由6个独立的模块组成，分别是CLC, walrus, cc, sc, nc, watch。 每个独立的模块可以安装在不同的机器上，也可以多个模块安装在一台机器上
- 每个模块都表现为一个django app
- 每个django app的数据库是mysql
- 模块之间的访问是通过web service来实现的，url表现形式如下
     <hostIP>/{clc | walrus | cc | sc | nc}/api/1.0/method_name/para1/para2/
- 系统提供一个统一的管理员WEB访问界面。

2.场景说明

2.1 用户场景说明
2.1.1 anonymouse场景说明
     只能使用公开的虚拟桌面资源。其使用方式限制为本地模式
2.1.2 user场景说明
     只能使用预定义好的虚拟桌面资源，其使用方式限制为远程模式
2.1.3 powerUser场景说明
     只能修改和使用预定义好的系统资源，其使用方式为远程模式

2.2 管理员场景说明
2.2.4 powerAdm
      可以管理（增加，删除，修改）和使用预定义好的系统资源，包括虚拟桌面和虚拟服务器
2.2.5 superAdm
      可以管理和使用一切系统资源

 
3.功能模块说明
3.1 CLC service
      实现了所有管理云平台的功能，包括
      - 监控系统健康状态：各服务的状态，各物理机器的状态
      - 查看各用户的资源使用状态：用户，组，和用户对应的instance状态
      - 系统运行参数配置和管理： 虚拟机机类型定义{}，网络参数设置{}，
      - 账户和访问控制管理
      - 资源管理
            - 镜像资源管理(增加，修改，删除，传送)
            - host资源管理(增加，修改，删除)
             - instance资源管理(增加，修改，删除，启动/停止，网络配置，监控策略，scalling 策略，LB策略)
             - IP地址资源管理(当前使用状态)
             - app资源管理（多个instance的组合）(增加，修改，删除，启动/停止)
      - 提供Adm和user和anonymouse的网页访问界面
      - 
3.2 WALRUS service
       - 实现了镜像文件管理: 增加，修改，删除
       - 对外提供web service，供CLC调用

3.3 CC service
       - 增加、删除NC
       - 调度instance到最适合的NC上运行
       - 定时汇报host，instance状态到CLC
       - 对外提供web service，供CLC调用

3.4 NC service
      -- 按照instance的定义，运行虚拟机（包括下载镜像，设定虚拟机网络参数，设定存储，设定运行模式，访问方式和监控模式）
      - - 对外提供web service，供CC调用

3.5 SC service
       - 为walrus提供物理 存储服务，
       - 提供WEB DAV服务
       - 对外提供web service，供其它机器调用调用

3.6 cloudWatch service
       - 

3.7 localNC service
      - 实现了本地虚拟桌面

4.系统信息流说明
4.1 pull信息流
      Clc会向walrus，sc直接请求相关系统状态信息
4.2 push信息流     
      Nc会主动向cc汇报系统状态信息
      Cc会主动向clc汇报系统状态信息

5.实现说明

5.1 每个host都包括：
       django project + 1-2 app + celery &  python based Rabitmq consumer service 
这意味着每个host都必须安装rabitmq服务，另外，其中一个rabitmq还必须作为公共的消息队列为云平台所有机器服务。

5.2 场景说明
5.2.1 NC/CC场景说明
       CC上安装rabitmq, CC所属的所有NC都使用CC上的rabitmq
       CC/NC执行异步任务是，简单的把celery的backend设置为CC上的rabitmq即可
       NC每次执行任务，其任务状态直接通过celery获取
       NC上存在一个daemon进程，定期收集系统状态信息，并发布到指定消息队列上
       CC上存在一个daemon进程，定期从指定的消息队列读取信息

5.2.2 CLC场景说明
      CC上存在一个daemon进程，定期发布到CLC的消息队列中；
      CLC上存在一个daemon进程，定期从指定的队列读取消息，处理后存放在memcache中，供后续的请求使用。
      
      
管理员任务台
1. 管理云平台	
    1.1 监控系统健康状态 
         --  service status view & change
    1.2 view user resource
       -- user, group, instance, ESB, etc
    1.3 网络配置管理
      -- 外部访问云平台各服务器的网络设置
      -- 外部访问虚拟机的网络设置
      -- 虚拟机之间的网络设置
    1.4 添加删除NC
2. 管理用户和组 （based on IAM）
   manages access control through an authentication, authorization, and accounting system. 
  This system manages 
      - user identities, 
      - enforces access controls over resources, and 
      - provides reporting on resource usage as a basis for auditing and managing cloud activities.
   2.1 






3. 资源管理
   3.1 compute resource(hosts & instances)
   3.2 walrus resource (image)
   3.3 IAM resource
   3.4 CloudWatch Resource
   3.5 ELB resource( load balance)
   3.6 Auto Scaling resource

4. 安全管理
5. 报告管理
5.1 instance report
5.2 S3 report
5.3 Elastic IP report
5.4 Capacity report

6. 镜像文件管理
6.1 上传、注册镜像文件
6.2 创建新的镜像文件
6.3 更新现有的镜像文件
6.4 删除镜像文件
  
7. CloudWatch Service
7.1 instance Metrics & Dimension
7.2 enable/disable monitoring





Task List:
----------------------------------------------
1. install memcach and python-memcache
2. build educloud memcache api
3. build daemon to communicate via rabbitmq: nc->cc->clc; walurs->clc, sc->cc


Host App Definition
1 NC
   web service: get request and run vm accordingly
   daemon:      collect host & instance status to cc

2 CC
   web service: get request to select a NC to run vm
   daemon:      collect host & NCs infor to clc

   there are 3 type of CC
   - cc for virtual server
   - cc for remote virtual desktop
   - cc for local virtual desktop

3 SC
   web service: get request to allocate storage and mount to NC
   daemon:      collect host info to CC

4 walrus:
    web service:  manage images files(add/upload, modify, remove, download)
    daemon:     collect host info to clc

5 clc
    web service: 
      1 admin web interface
      2 user web interface
    daemon:     collect host info & all other component info into memcache

Module Definition
1. luhyaapi module
2. luhyadb module
   all database definitions are here.
   - eduServer db
   - image db
   - instance db
   - build task db
   - sync task db

A few Typical Scenario
1. user login
2. watch educloud status
3. list all eduServer
4. list all images
5. list all active instance
6. list all tasks
7.

