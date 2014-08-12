alter table clc_ecserverrole convert to character set utf8;
INSERT INTO clc_ecserverrole (`ec_role_name`, `ec_role_value`) VALUES ("cloud controller",    "clc");
INSERT INTO clc_ecserverrole (`ec_role_name`, `ec_role_value`) VALUES ("images controller",   "walrus");
INSERT INTO clc_ecserverrole (`ec_role_name`, `ec_role_value`) VALUES ("cluster controller",  "cc");
INSERT INTO clc_ecserverrole (`ec_role_name`, `ec_role_value`) VALUES ("node controller",     "nc");
INSERT INTO clc_ecserverrole (`ec_role_name`, `ec_role_value`) VALUES ("storage controller",  "sc");
