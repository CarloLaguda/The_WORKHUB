sudo apt update
sudo apt install mariadb-server -y
sudo service mariadb start
sudo mariadb
pip install -r .devcontainer/requirements.txt
sudo npm install -g @angular/cli
python3 WorkHub/server/main.py
python3 WorkHub/server/routes/users_route.py
