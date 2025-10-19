sudo apt update
sudo apt install mariadb-server -y
cp .env.example .env
sudo service mariadb start
sudo mariadb
pip install -r .devcontainer/requirements.txt
python3 WorkHub/server/main.py
sudo npm install -g @angular/cli
cd WorkHub
sudo npm install
cd ..
