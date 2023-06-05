CREATE TABLE abilities ( 
	ability_id           INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT(100)     ,
	attack_change        INTEGER  DEFAULT 0   ,
	base_stat            TEXT     ,
	class_required       INTEGER     ,
	race_required        INTEGER     ,
	defense_change       INTEGER  DEFAULT 0   ,
	magic_change         INTEGER  DEFAULT 0   
 );

CREATE TABLE classes ( 
	class_id             INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT(100)     ,
	description          TEXT     ,
	health_modifier      INTEGER     ,
	attack_modifier      INTEGER     ,
	defense_modifier     INTEGER     ,
	magic_modifier       INTEGER     
 );

CREATE TABLE enemy ( 
	enemy_id             INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT(100) NOT NULL    ,
	created_at           DATETIME     ,
	updated_at           DATETIME     
 );

CREATE TABLE enemy_abilities ( 
	id                   INTEGER NOT NULL  PRIMARY KEY  ,
	enemy_id             INTEGER NOT NULL    ,
	ability_id           INTEGER NOT NULL    ,
	required_level       INTEGER     ,
	FOREIGN KEY ( enemy_id ) REFERENCES enemy( enemy_id ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( ability_id ) REFERENCES abilities( ability_id ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE enemy_stats ( 
	enemy_id             INTEGER NOT NULL  PRIMARY KEY  ,
	level                INTEGER  DEFAULT 0   ,
	health               INTEGER     ,
	attack               INTEGER     ,
	defense              INTEGER     ,
	magic                INTEGER     ,
	experience           INTEGER     ,
	FOREIGN KEY ( enemy_id ) REFERENCES enemy( enemy_id ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE items ( 
	item_id              INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT(100)     ,
	description          TEXT     ,
	base_stat_effect     INTEGER  DEFAULT 0   ,
	status               INTEGER     ,
	status_effect        INTEGER     ,
	base_stat            INTEGER     
 );

CREATE TABLE levels_experience ( 
	id                   INTEGER NOT NULL  PRIMARY KEY  ,
	level                INTEGER NOT NULL    ,
	experience_required  INTEGER NOT NULL    ,
	ability_gained       INTEGER     
 );

CREATE TABLE races ( 
	race_id              INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT(100)     ,
	description          TEXT     ,
	health_modifier      INTEGER     ,
	attack_modifier      INTEGER     ,
	defense_modifier     INTEGER     ,
	magic_modifier       INTEGER     
 );

CREATE TABLE statuses ( 
	status_id            INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT(100)     ,
	description          TEXT     ,
	base_stat            INTEGER     ,
	base_stat_effect     INTEGER     
 );

CREATE TABLE enemy_items ( 
	enemy_item_id        INTEGER NOT NULL  PRIMARY KEY  ,
	enemy_id             INTEGER NOT NULL    ,
	item_id              INTEGER NOT NULL    ,
	quantity             INTEGER  DEFAULT 0   ,
	drop_percent         INTEGER NOT NULL DEFAULT 0   ,
	FOREIGN KEY ( enemy_id ) REFERENCES enemy( enemy_id ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( item_id ) REFERENCES items( item_id ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE player ( 
	player_id            INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT(100)     ,
	created_at           DATETIME     ,
	updated_at           DATETIME     ,
	class_id             INTEGER NOT NULL    ,
	race_id              INTEGER NOT NULL    ,
	FOREIGN KEY ( class_id ) REFERENCES classes( class_id ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( race_id ) REFERENCES races( race_id ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE player_abilities ( 
	player_id            INTEGER NOT NULL    ,
	ability_id           INTEGER NOT NULL    ,
	required_level       INTEGER     ,
	CONSTRAINT unq_player_abilities_ability_id UNIQUE ( ability_id ),
	FOREIGN KEY ( ability_id ) REFERENCES abilities( ability_id ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( player_id ) REFERENCES player( player_id ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE player_items ( 
	player_item_id       INTEGER NOT NULL  PRIMARY KEY  ,
	player_id            INTEGER NOT NULL    ,
	item_id              INTEGER NOT NULL    ,
	quantity             INTEGER     ,
	FOREIGN KEY ( player_id ) REFERENCES player( player_id ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( item_id ) REFERENCES items( item_id ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE player_stats ( 
	player_id            INTEGER NOT NULL  PRIMARY KEY  ,
	level                INTEGER  DEFAULT 0   ,
	health               INTEGER     ,
	attack               INTEGER     ,
	defense              INTEGER     ,
	magic                INTEGER     ,
	experience           INTEGER     ,
	status               INTEGER     ,
	FOREIGN KEY ( player_id ) REFERENCES player( player_id ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( status ) REFERENCES statuses( status_id )  
 );

