drop table if exists users;
drop table if exists boards;
drop table if exists teams;

create table users (
  no integer primary key autoincrement,
  id text not null,
  username text not null,
  password text not null,
  email text not null,
  mobile text not null,
  curteam text
);

create table boards (
  no integer primary key autoincrement,
  id text not null,
  btype integer not null,
  ctype text not null,
  subject text not null,
  content text not null,
  username text not null,
  writedate text not null,
  shared integer not null
);

create table teams (
  no integer primary key autoincrement,
  name text not null,
  notice text,
  password text not null
);

insert into users (id, username, password, email, mobile) values ("admin", "admin", "11111111", "69277660@naver.com", "010-7525-7044");