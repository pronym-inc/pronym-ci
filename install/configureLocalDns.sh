echo "Configuring local DNS..."
grep -qxF "127.0.0.1   pronymservicetemplate.local" /etc/hosts || echo '127.0.0.1   pronymservicetemplate.local' | sudo tee -a /etc/hosts
