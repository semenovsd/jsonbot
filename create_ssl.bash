# Create ssl certificate
. .env
mkdir "${SSL_DIR}"
openssl req -newkey rsa:2048 -sha256 -nodes -keyout "${SSL_DIR}${SSL_PRIV}" -x509 -days 365 -out "${SSL_DIR}${SSL_CERT}" \
-subj "/C=US/ST=Oregon/L=Portland/O=Company Name/OU=Org/CN=${DOMAIN_NAME_OR_IP}"
sudo chmod -R +r "${SSL_DIR}"
