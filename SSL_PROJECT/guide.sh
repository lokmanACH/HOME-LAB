echo "we are in the guide.sh script"
echo "at first we have to install nginx and openssl"
sudo apt update
sudo apt install nginx openssl -y

echo "check openssl and nginx version"
openssl version
nginx -v

echo "start and enable nginx service"
sudo systemctl start nginx
sudo systemctl enable nginx


echo "create a ssl folder and generate a self-signed certificate"
sudo mkdir -p /etc/nginx/ssl

# Generate a private key
sudo openssl genrsa -out /etc/nginx/ssl/nginx.key 2048
sudo chmod 600 /etc/nginx/ssl/nginx.key


# Generate a self-signed certificate
sudo openssl req -x509 \
  -new \
  -key /etc/nginx/ssl/nginx.key \
  -sha256 \
  -days 365 \
  -out /etc/nginx/ssl/nginx.crt


echo "configure nginx to use the self-signed certificate"