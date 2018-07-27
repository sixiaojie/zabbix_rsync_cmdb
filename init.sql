CREATE DATABASE if not EXISTS pull;
use pull;
creata table if EXISTS hosts(
  id int not null auto_increment;
  hostid int not null,
  hostname varchar(30) not null,
  groupid int not null,
  PRIMARY KEY (id)
)


create table groups(
  id int not null auto_increment,
  groupid int not null,
  groupname varchar(30) not null,
  PRIMARY KEY (id)
)

creata table usergroup(
  id int not null auto_increment,
  usergroupid int not null,
  usergroupname VARCHAR,
  PRIMARY KEY (id)
)