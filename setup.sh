# Setup the database for dev and test
sudo -u postgres bash -c "psql < /home/ali/fullstackdevelop/FSND/AliProjects/02_trivia_api/starter/backend/setup.sql"

# Connect to trivia db, create necessary tables and add some data to dev db
sudo -u postgres bash -c "psql trivia < /home/ali/fullstackdevelop/FSND/AliProjects/02_trivia_api/starter/backend/trivia.psql"