#! /bin/bash
mysql -uroot -proot mysql < ecauthpath.sql
mysql -uroot -proot mysql < ecaccount.sql
mysql -uroot -proot mysql < ecccresources.sql
mysql -uroot -proot mysql < ecclusternetmode.sql
mysql -uroot -proot mysql < ecostypes.sql
mysql -uroot -proot mysql < ecserverrole.sql
mysql -uroot -proot mysql < ecservers.sql
mysql -uroot -proot mysql < ecvmtypes.sql  
mysql -uroot -proot mysql < ecvmusages.sql


