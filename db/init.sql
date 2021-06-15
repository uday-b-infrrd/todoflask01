CREATE DATABASE flaskapp;

use flaskapp;

CREATE TABLE todo(
    id integer auto_increment,
    content varchar(200) not null,
    date_created date,
    primary key(id)
);