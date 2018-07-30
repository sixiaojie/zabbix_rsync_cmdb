CREATE DATABASE if not EXISTS pull;
use pull;
creata table if EXISTS hosts(
  id int not null auto_increment;
  hostid int not null,
  ip VARCHAR not null,
  hostname varchar(30) not null,
  groupid VARCHAR not null,
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

create table mediatype(
  id int not null auto_increment,
  mediaid int not null,
  type int not null,
  medianame varchar(20) not NULL,
  PRIMARY KEY (id)
)

create table user(
  id int not null auth_increment,
  userid int not,
  username varchar(20) not null,
  passwd varchar(30) not null,
  media varchar not nulll,
  PRIMARY KEY (id)
)