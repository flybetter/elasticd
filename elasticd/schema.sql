DROP TABLE  if EXISTS settings;
create table settings(
  id INTEGER PRIMARY KEY autoincrement,
  title text not NULL ,
  content text not NULL
)