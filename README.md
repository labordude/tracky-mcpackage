flatiron mine

db tables:
player: id, name, level, health, attack, defense, experience, player_ability_link: id, player_id FK, special_abilities FK

enemy: id,level, health, attack, defense, experience
item: id, name, type, power, description

special_abilities: id, name, attack, defense, description
enemy_abilities: id
dungeon


world :Flatiron mines based on 

item objects are dictionaries

if player is level x, select * from special_abilities where level_required <= x AND whatever class/race/etc required# tracky-mcpackage
