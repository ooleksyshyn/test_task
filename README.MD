## Project requirements
 - mysql
 - python >= 3.6
 - python packages from requirements.txt
 
## To launch project
 
### Create database setup
  - mysql -e 'CREATE DATABASE `testdb`;'
  - mysql -e 'CREATE USER oleksii@localhost IDENTIFIED BY "1";'
  - mysql -e 'GRANT ALL PRIVILEGES ON testdb.* TO oleksii@localhost;'
  - mysql testdb < db/main_db_bootstrap.sql


### Install requirements
  - pip3 install -r requirements.txt

### Run script
  - python -m src


### Test script
  - python -m unittest discover tests/
