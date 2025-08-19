# TODO


### Writeup Ideas 
- [ ] Difference between pro and amateur CS
- [ ] GGs per game

### Code Ideas
- [x] Add util table to DB
 - grenade type
 - pop position
 - throw position
 - air time
 - players flashes / damage
- [ ] Create visualizations for kills
 - [ ] Per person / team / weapon
- [x] Add bomb plants table

### Bug Fixes
- [ ] Trade / traded columns in kill table don't lineup
 - This is just because 2 deaths can count for 1 trade kill and vice versa

### In Progress
- [ ] Build out website GUI
- [x] Initial player spread per round (2-1-2, etc)
 - [ ] Win rates for different setups, in different types of buys, etc

### Done ✓
- [x] Add damages table to DB
- [x] Add weapon fires table to DB
- [x] Add positional data to DB
 - [x] damage - Attacker and Victim positions
 - [x] kill - attacker and victim positions
 - [x] weapon_fire - player position and direction
- [x] Add ticks for events in DB
 - [x] kill
 - [x] message


## General Analytics Goals
CSC - CSC / ESEA has the data, just need queries for it
SQL - We have the data, just need queries / visualizations for it
DB - Need to add things to the database

### Predictive / Team Scouting
- (CSC) Map Bans
- (SQL) Avg T Side Round Time
 - Pistols rounds / eco rounds / buy rounds
- (SQL)(DB) Defaults, need to improve logic for defaults
- (DB) Plants, which site, when general preferences and plant spots
- (DB) Common utility thrown at different parts of the round (early round, mid round, post plants, etc)
- (SQL) Common angles, strong KD angles, etc

### Performative / Player Scouting
- (SQL) General rating
- (SQL or DB) KAST
- (SQL) Expected KD

### Diagnostic / Player and Team Improvement
- (SQL) Strong / weak guns
- (SQL) Strong / weak distances (in context of guns in duel)
- (SQL) Strong / weak positions on maps