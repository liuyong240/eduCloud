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






------------------
I System Overview
------------------

there are 3 category scenarios, and 3 kinds of resouceshosts, images, instances) :

1. manage virtual server

  - create image based on template;
  - submit image;
  - modify image;
     - version management
  - set image para:
     - name, OS type, 32bit/64bit, usage(desktop/server), owner-group, description, version, pubDate, size   
  - create instance, and set vm para;
     - VM Type para - memory, disk, cpu, network(manage IP, access IP, internal IP, etc)
     - runtime para - host server(IP or any), access mode/para, starup para(vbox only), version, persistent/temperary etc
     - metrics para - CPU/DISK/NETWORK/alive
     # below para need set nginx proxy on CC for loadbalance/HA/scale 
     - HA:       acive vs active, active vs standby
     - scale:    default number of instance, maximum number of instance
     - run/stop vm;
       - auto vs manual
  - monitor vm; collect all metrics data

2. manage remote virtual desktop

   - create image based on template;
   - submit image;
   - modify image;
     - version management
   - set image para:
     - name, OS type, 32bit/64bit, usage(desktop/server), owner-group, description, version, pubDate, size
   - create vm instance, and set vm para;
     - VM Type para - memory, disk, cpu, network(manage IP, access IP, internal IP, etc)
     - runtime para - host server(IP or any), access mode/para, starup para(vbox only), version, persistent/temperary, auto-shutdown, etc
     - metrics para - CPU/DISK/NETWORK/alive
   - pull image;
   - run/stop vm; 
   - monitor vm; collect all metrics data  

3. manage local virtual desktop

   - create image based on template;
   - submit image;
   - modify iamge;
     - version management
   - set image para:
     - name, OS type, 32bit/64bit, usage(desktop/server), owner-group, description, version, pubDate, size
  create vm instance, and set vm para;
     - VM Type para - memory, disk, cpu, network(manage IP, access IP, internal IP, etc)
     - runtime para - host server(IP or any), access mode/para, starup para(vbox only), version, persistent/temperary etc
     - metrics para - CPU/DISK/NETWORK/alive
   - push/pull image;
   - run/stop vm; 
   - monitor vm; collect necessary metrics data

3. manage server/Host

   - add physical server/host;
   - set host para;
     - IP, MAC(for wake on LAN), name, location, owner-group(definiton as : edu.cloud.longyou.country.school.class.room),
     - physical para: memory, disk,
     - run-time option(valid only for local host): 
       -  autoSync, autoPoweroff, offlineEnabled, isPad,   
  
--------------------------
II Adminstrator's Scenario
--------------------------

1. owner-group definiton

   - the authorization value of owner group looks like "edu.cloud.longyou.country.school.class.room.xxx.yyy.zzz", and can be extend unlimited.
   - the account belongs to owner-group "aaa.bbb" can access resource belongs to "aaa.bbb.*";
   - the account belongs to owner-group "aaa.bbb.ccc" can NOT access resource belongs to "aaa.bbb"
   - besides authorization, there are permission associated to owner group "read, write, execute, create, delete, full" 
   - each permison created for one type of resource (host, image, instance, etc)
   - finally, the owner group will looks like below:
     - name: any string
     - auth: aaa.bbb.ccc.ddd.*
     - permission:
       - host:    None, {read | write | execute | create | delete }, Full
       - image:   None, {read | write | execute | create | delete }, Full
       - instance:None, {read | write | execute | create | delete }, Full

2. Administrator's tasks
   - admin watch system status
   - admin manage images
     - read image properties
     - add/modify image content & properties
       - this is a special instance, and associated with different properties.
     - delete image
   - admin manage hosts/servers
     - manage hosts
       - there are only one kinds of hosts need to be managed, the one that run VM locally.
       - host will auto be added when powered on.
       - host will send heartbeat to its CC every 5 minutes(configurable) via rabbitmq message queue
       - host will publish its status data to CC  if there are any change
       - host and its CC should be same LAN
       - admin can pull data from host if necessary
       - admin can read/modify host properties
       - admin can delete host
       - admin can power on/off host remotely
     - manage servers
       - there are 5 kinds of servers: clc, walrus, cc, nc, sc
       - server will auto be added when power on.
       - severr will send heatbeat, and publish its status data(if any change) to its boss via rabbitmq message queue
          - clc's boss    - clc 
          - wlaurs's boss - clc
          - cc's boss     - clc
          - nc's boss     - cc
          - sc's boss     - cc
       - admin can pull data from server if necessary
       - admin can remove server ( how to deal with multipl walrus ? )
   - admin manage instances
     - manage server instance
       - admin can create/modify/run/stop/delete instance
     - manage remote desktop instance
       - admin can create/modify/run/stop/delete instance
     - manage local desktop instance
       - admin can create/modify/run/stop/delete instance
       - admin can push instance to its host

------------------
II User's Scenario
------------------
There are 3 kinds of users:
- user of virtual server, not discussed here
- user of remote virtual desktop, 
- anonymouse user of local virtual desktop,

2.1 URVD
- login CLC URVD portal web page
- find his/her instance
- start instance
- connect to instance
- working
- disconnect instance
- stop instance

2.2 AULVD
- power on the host
- based on host's CC owner-group, list all available instance
- run selected instance (download from walrus to CC for cache, and sync to host when running)
- stop instance
- power off host


---------------------
III  initialization
---------------------
when ecCloud is installed, the next step is to initialize it with database table and insert some init data, so that system can be ready for running.

3.1 create tables
    either "python manage.py syncdb" or below 3 commands:
    python manage.py syncdb --noinput
    python manage.py createsuperuser --username=luhya --noinput --email luhya@hoe.com
    python manage.py changepassword luhya
    
3.2 insert data into tables
    python manage.py sqlcustom
    it will ooks for the file <appname>/sql/<modelname>.sql to run when "python manage.py syncdb" call "CREATE TABLE".

-----------------------------------------------
IV  WEB Service and Message management
-----------------------------------------------
4.1 software components description  
- clc:    web server, memcache, daemon, rabbitmq(status-queue and its consumer)
- walrus: web server, daemon, rsyncd
- cc:     web server, daemon, rabbitmq(status-queue and its consumer, cmd-queue), dhcp, iptales, rsyncd
- nc:     [web server], daemon, cmd-queue's consumer, and task-worker-thread

4.2 queue definition
rabitmq is used in this system for distributed task initiate and task status report.
so at each rabitmq,

4.2.1 CLC
- a "command' queue and consumer daemon,
- a "system_status" queue and consumer daemon read data and write to memcache (http request re-direct memcache)
- each task-related queue,

4.3 scenario description

4.3.0 pre-condition
clc/walrus/cc/nc/sc daemon start and register themselves to clc  : 
  - /clc/register/cc/ccname
  - /clc/register/walrus
  - /clc/register/nc/ccname or /clc/register/nc
each node has a few conf file :
walrus: /storage/config/clc.conf
cc:     /storage/config/clc.conf
nc:     /storage/config/clc.conf, cc.conf(option)

the content of conf is :  IP='xxx.xxx.xxx.xxx'

4.3.1 image build

task definition: 
# all op & status belongs to one transaction ID
  transaction ID = 'srcid:destid:instanceid' example : img-37eefa34:img-29aeffee:ins-abcdefa5
  memcache data struct:  
     - key   = transaction ID
     - value = {
        'phase'     : 'downloading', 'cloning', 'pending', 'running', 'stop', 'stopped', 'submit', 'submitting', 'submitted'
        'progress'  : integer, 
        'aURL'      : ip:port
        'message'   :  
        'ccip'      :
        'ncip'      :
       }
  status_queue message data struct:
     - 'tid'     :
     - 'phase'   :
     - 'progress':
     - 'aURL'    : 
     - 'message' :
  cmd_queue message data struct:
     - 'op' : { 'image_build', 'image_modify', 'run_vs', 'run_rvd', 'run_lvd' } 
     - 'tid : 
  
  each CC server should be set a property as "run vs", or "run lvd" or "run rvd"
  when create instance, it also has a property as 'vs', or 'lvd', or 'rvd'  
  each instance can be assigend ccname, but it is optional
  imagebuild & imagemodify instance belongs to either vs or rvd, based on image usage
  
- clc.view get the request, 
  - send request to cc, 
  - and return a wizard page, this page is divided into 3 phase
    - preparing phase : only display the status (by getting status data from memcache/db)
    - running & editing phase : provide run & stop button (by getting the status data from memcache/db)
    - submitting phase: provide submit button and display the status ( by getting status data from memcache/db) 
- cc.view get the request,
  - send cmd to cmd_queue
  - and return back "OK"
- nc daemon get the cmd message from cmd_queue
  - perform download phase:
    CC download phase
    - ask CC to download image from walrus by RPC
    - get the status data from anonymouse reply queue, and send it to cc's status queue, until completed
    - send a cmd to cmd_queue to start NC download phase
    NC download phase
    - start thread to download image from CC,
    - report status date to CC's status queue, until completed
    - send a cmd to cmd_queue to start NC clone phase
  - perform NC clone phase
    - start to clone a new image
    - report status date to CC's status queue until completed
  
  - perform run instance operation:
    - report status data to CC's status queue until VM is running
  - perform stop instance operation:
    - report status data to CC's status queue until VM is stopped
  - perform submit instance operation:
    NC upload phase:
    - start thread to upload image to CC
    - report upload progress to CC's status queue until completed
    - send a cmd to cmd_queue to start CC upload phase
    CC upload phase:
    - ask CC to upload image to walrus by RPC
    - get the status data from anonymouse reply queue, and send it to cc's status queue until completed



4.3.2 image modify

4.3.3 Vritual server running

4.3.4 Remote virtual desktop running

4.3.5 Local virutal desktop running


-----------------------------------------------
V  Network management
-----------------------------------------------
5.1 Pre-condition

- CLC/CCs are in one network, CC/NCs are in one network, they can be two independent network
- CLC, CCs are configured with public static IP addr
- NCs are configured with public/private static IP addr (PUBLIC mode vs PRIVATE mode)

5.2 Network Mode

5.2.1 Local Virutal Desktop

- NC has static valid IP addr that is managed by 3rd party
- VM runs on NC in NAT mode, 
- user access VM from NC directely
- VM access internet by NC (NC is able to access internet)

5.2.2 Remote Virtual Desktop(only need port resource allocation)

- In PUBLIC mode, each NC has a public IP addr 
  - VM runs on NC in NAT mode
  - user access VM by NC.ip:port
  - VM access internet by NC (NC is able to access internet)

- In PRIVATE mode, each NC has a private IP addr
  - VM runs on NC in NAT mode
  - user access VM by CC.ip:port, and iptable forwarding it to NC.ip:port
  - VM access internet by NC (NC is able to access internet)
  - CC is responsible to manage port assignment
    
5.2.3 Virutal Server

Each VS has a PUBLIC IP assigned for access, and these public IP addr is managed by CC's DHCP 

- In PUBLIC mode, each NC has a public IP addr
  (need public IP pool for VM service, itself, managed by CC DHCP )
  (need port resouce for VM management)
  - VM runs on NC in bridge mode with assigned Public IP & MAC
  - user access VM by pubIP:port(80)
  - VM access internet by NC (NC is able to access internet)


- In PRIVATE mode, each NC has a private IP addr
  sudo ifconfig eth0:1 10.0.0.100 broadcast 10.0.0.255 netmask 255.255.255.0
  (need public IP pool for VM service, assigned to CC by IP alias cmd above )
  (need private IP pool for VM service, managed by CC DHCP)
  (need port resouce for VM management)
  - CC also manage VMs private IP & mac by its DHCP server
  - VM runs on NC in bridge mode with assigned Private IP & MAC
  - CC add interface alias with related Public IP addr
  - user access VM by CC.pubIP:port, and iptable forwarding it to NC.priIP:port
  - VM access internet by NC (NC is able to access internet)

==========================
VI Data structure
==========================

6.1 cmd definition

6.1.1 cmd from cc to nc

{
    'type'  : 'cmd',
    'op'    : 'image/create', 'image/modify', 'image/run', 'image/stop', 'image/submit',
    'paras' :  tid
}

6.1.2 (RPC)
cmd from nc to cc
{
    'type'  : 'cmd',
    'op'    : 'image/prepare', 'image/run', 'image/stop', 'image/submit',
    'paras' :  tid
}
result from cc to nc
{
    'type'      : 'taskstatus',
    'phase'     : "downloading", "editing", "submitting"
    'progress'  : progress,
    'vmstatus'  : 'init', 'running', 'stopping', 'stopped'
    'tid'       : tid
    'errormsg'  : ''
}

6.1.3 status report message (from nc to cc, from cc to nc)
{
    'type'      : 'taskstatus',
    'phase'     : "downloading", "editing", "submitting"
    'progress'  : progress,
    'vmstatus'  : 'init', 'running', 'stopping', 'stopped'
    'tid'       : tid
}
{
    'type'      : 'nodestatus',
    'ip'        :
    'role'      :

}
{
    'type'      : 'hoststatus',

}
{
    'type'      : 'insstatus',
}

6.1.3 VM runtime options
{
    # general
    'ostype'            :
    'usage'             :
    # hardware
    'memeory'           :
    'cpus'              :
    'disk_type'         :
    'audio_para'        :
    # network
    'netwowrkcards'     :
    [
        { 'nic_type': "", 'nic_mac': "" , 'nic_ip': ""},
        { 'nic_type': "", 'nic_mac': "" , 'nic_ip': ""},
        { 'nic_type': "", 'nic_mac': "" , 'nic_ip': ""},
        ... ...
    ]
    'publicIP'          :
    'privateIP'         :
    'rdp_port'          :
    'services_ports'    : [ ... ...]
    'accessURL'         : []
    'mgr_accessURL'     :
    'run_with_snapshot' : 1, 0
    'iptable_rules'     :
    [
        'rule1',
        'rule2',
        ... ...
    ]
}

VII CC's resource

  Ubuntu RDP client : remmina

7.0 CC network mode
    PUBLIC  Mode: NC can be accessed from outside
    PRIVATE Mode: NC can NOT be accessed from outside, need CC as bridge

7.1 VM Network resource

# VD only need this
7.1.1 RDP Port pool
  CC PUBLIC  Mode:  accessURL = NCIP:port
  CC PRIVATE Mode:  accessURL = CCIP:port, and forward to NCIP:port

# below are only for VS
7.1.2 Public IP address pool
7.1.3 Private IP address pool (managed by CC DHCP server)
7.1.4 MAC addr pool (managed by CC DHCP server)

  CC PUBLIC  Mode:
    PUBLIC IPs = PRIVATE IPS
    MAC addr assigned to VM, and get IP from DHCP server's private IP pool by MAC
    accessURL = PUBLICIP:rdp_port|80

  CC PRIVATE Mode:  accessURL = CCIP:port, and forward to NCIP:port
    PUBLIC IPs = PRIVATE IPS
    MAC addr assigned to VM, and get IP from DHCP server's private IP pool by MAC
    add Public IP to cc as IP alias
    add iptable rule as PUBLICip:port => PRIVATEIP:port
    accessURL = PUBLICIP:rdp_port|80

VIII. What happens when you run a vm ?

8.1 when you create/modify a new image
- select a image, click "create"/"modify" button
- browser will send request /clc/image/create/task/begin/(?P<srcid>\w+) to clc
- clc will do below things
  - generate tid
  - add a new record to ectaskTransaction
  - display clc/wizard/image_create_wizard.html
- then user click "prepare" button on wizard page
  - send request /clc/image/create/task/prepare/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$ to clc
  - clc pick a cc, and send request /cc/api/1.0/image/create/task/prepare to it with tid.
  - cc response with picked nc ip, and clc save ccip & ncip into ectaskTransaction
  - cc work together with nc to download from walrus to cc and then to nc
    - during this time, nc will report progress status to cc, and cc forward to clc
    - user can access status info by request /clc/image/create/task/getprogress/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$
- then user click "run" button on wizard page
  - send request /clc/image/create/task/run/(?P<srcid>\w+)/(?P<dstid>\w+)/(?P<insid>\w+)$ to clc
  - clc update ectaskTransaction records with new phase
  - clc prepare the runtime_option and POST request /cc/api/1.0/image/create/task/run to cc
    POST DATA = {tid, ncip, runtime_opiton}
  - cc then do below things
    - send 'image/run' command to nc with message {runtime_option}
    - add iptable rules if there are
  - nc get 'image/run' command
    - downlaod image and report progress
    - run image and report status



8.2 when you define a new instance
8.2.1 define VS
8.2.2 define VD
8.2.3 define LVD

8.3 when you run a new instance
8.3.1 run VS
8.3.2 run VD
8.3.3 run LVD


lvd cluster - public

rvd cluster
  - public
    prot range = ncip:port

  - private
    public IP + private IP + port = ccip:port => ncip:port

vs cluster
  - manual
    => manual => vm public IP
    => RDP URL : ncip:port
    => server URL: vm publicIP:port

  - public dhcp
    public IP + port  =>
    => vm mac => dhcp => vm public IP
    => RDP URL : ncip:port
    => server URL: publicIP:server port

  - private dhcp
    public IP + private IP + port


When nc start, it should to sshfs cc's /storage/data directory as below:

sshfs [user@]host:[dir] mountpoint [options]
前面和ssh命令一样，mountpoint是挂载点
options重点关注下：
-C 压缩，或者-o compression=yes
-o reconnect 自动重连
-o transform_symlinks 表示转换绝对链接符号为相对链接符号
-o follow_symlinks 沿用服务器上的链接符号
-o cache=yes
-o allow_other 这个参数最重要，必须写，否则任何文件都是Permission Deny


#相关代码
sshfs -o cache=yes,allow_other user@xx.xx.xx.xx:/dir_remote ./dir_local
fusermount -u mountpoint


Some Issues:
- Doen: rvd need add public & provate network mode
- Doen: when vm get into running, stopped state, wizard web page need to update clc's db
- delete snapshot before submitting
- wizard always contains 3 steps.
- when submit finished, nc send message to cc to
  1. delete task thread in cc.tasks_status
  2. delete task thread in cc.

  cc then send rquest to clc, to
  1. add a new image record, and set it properties
  2. delete transaction record
