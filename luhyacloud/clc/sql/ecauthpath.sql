alter table clc_ecauthpath convert to character set utf8;
INSERT INTO clc_ecauthpath (`ec_authpath_name`, `ec_authpath_value`) VALUES ("云平台管理员", "eduCloud.admin");
INSERT INTO clc_ecauthpath (`ec_authpath_name`, `ec_authpath_value`) VALUES ("教育局管理员", "eduCloud.edu-depart.admin");
INSERT INTO clc_ecauthpath (`ec_authpath_name`, `ec_authpath_value`) VALUES ("教育局员工",   "eduCloud.edu-depart.employee");