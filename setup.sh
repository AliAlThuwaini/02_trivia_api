# Setup the database for dev and test
sudo -u postgres bash -c "psql < /home/ali/FSNDAliProjects/02_trivia_api/backend/setup.sql"

# Connect to trivia db, create necessary tables and add some data to dev db
sudo -u postgres bash -c "psql trivia < /home/ali/FSNDAliProjects/02_trivia_api/backend/trivia.psql"