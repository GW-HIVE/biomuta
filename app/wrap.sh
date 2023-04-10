sudo systemctl stop docker-biomuta-app-tst.service
python3 create_app_container.py -s tst
sudo systemctl start docker-biomuta-app-tst.service

