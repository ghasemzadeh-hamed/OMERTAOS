#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] This installer must be run as root (try sudo)." >&2
  exit 1
fi

if [[ ! -f /etc/os-release ]]; then
  echo "[ERROR] Unsupported distribution (missing /etc/os-release)." >&2
  exit 1
fi

source /etc/os-release
if [[ ${ID,,} != "ubuntu" && ${ID,,} != "debian" && ${ID_LIKE,,} != *"debian"* ]]; then
  echo "[ERROR] Only Debian/Ubuntu style systems are supported." >&2
  exit 1
fi

APACHECTL=$(command -v apache2ctl || true)
if [[ -z "$APACHECTL" ]]; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y apache2
else
  apt-get update
fi

DEBIAN_FRONTEND=noninteractive apt-get install -y certbot python3-certbot-apache dnsutils

for module in proxy proxy_http proxy_wstunnel headers ssl http2 rewrite; do
  a2enmod "$module" >/dev/null 2>&1 || true
done

detect_ip() {
  local proto="$1"
  local ip=""
  if command -v dig >/dev/null 2>&1; then
    if [[ "$proto" == "v4" ]]; then
      ip=$(dig +short -4 myip.opendns.com @resolver1.opendns.com || true)
    else
      ip=$(dig +short -6 myip.opendns.com aaaa @resolver1.opendns.com || true)
    fi
  fi
  if [[ -z "$ip" ]]; then
    if [[ "$proto" == "v4" ]]; then
      ip=$(curl -4 -fsS https://api.ipify.org || true)
    else
      ip=$(curl -6 -fsS https://api64.ipify.org || true)
    fi
  fi
  echo "$ip"
}

PUBLIC_IPV4=$(detect_ip v4)
PUBLIC_IPV6=$(detect_ip v6)

echo "Detected public IPv4: ${PUBLIC_IPV4:-unavailable}"
echo "Detected public IPv6: ${PUBLIC_IPV6:-unavailable}"

default_mode="Domain"
read -rp "Select mode ([Domain]/Local): " MODE
MODE=${MODE:-$default_mode}
MODE=${MODE,,}
if [[ "$MODE" != "domain" && "$MODE" != "local" ]]; then
  echo "[ERROR] Mode must be Domain or Local." >&2
  exit 1
fi

ROUTING="subdomains"
DOMAIN=""
EMAIL=""
USE_IPV6="no"

if [[ "$MODE" == "domain" ]]; then
  while [[ -z "$DOMAIN" ]]; do
    read -rp "Enter the primary domain (e.g. aion.example.com): " DOMAIN
    DOMAIN=${DOMAIN,,}
  done
  read -rp "Routing style ([subdomains]/paths): " ROUTING_INPUT
  ROUTING_INPUT=${ROUTING_INPUT:-$ROUTING}
  ROUTING=${ROUTING_INPUT,,}
  if [[ "$ROUTING" != "subdomains" && "$ROUTING" != "paths" ]]; then
    echo "[ERROR] Routing style must be subdomains or paths." >&2
    exit 1
  fi
  read -rp "Email for Let's Encrypt notifications: " EMAIL
  while [[ -z "$EMAIL" ]]; do
    echo "Email is required for Let's Encrypt." >&2
    read -rp "Email for Let's Encrypt notifications: " EMAIL
  done
  read -rp "Enable IPv6 listener? ([y]/n): " USE_IPV6_INPUT
  USE_IPV6_INPUT=${USE_IPV6_INPUT:-y}
  if [[ ${USE_IPV6_INPUT,,} == "y" || ${USE_IPV6_INPUT,,} == "yes" ]]; then
    USE_IPV6="yes"
  fi

  echo "\nDNS lookup for ${DOMAIN}:"
  dig +noall +answer "$DOMAIN" || true
  if [[ "$ROUTING" == "subdomains" ]]; then
    for sub in console api control; do
      echo "-- ${sub}.${DOMAIN} --"
      dig +noall +answer "${sub}.${DOMAIN}" || true
    done
  fi
  if [[ "$USE_IPV6" == "yes" ]]; then
    AAAA=$(dig +short AAAA "$DOMAIN" || true)
    if [[ -z "$AAAA" ]]; then
      echo "[WARN] No AAAA record detected for ${DOMAIN}; disable IPv6 or add an AAAA record." >&2
    fi
  fi
fi

APACHE_DIR=/etc/apache2
SITES_AVAILABLE="$APACHE_DIR/sites-available"
mkdir -p "$SITES_AVAILABLE"

create_vhost_file() {
  local name="$1"
  shift
  cat <<CONF >"$SITES_AVAILABLE/$name.conf"
$*
CONF
}

PROXY_TIMEOUT="ProxyTimeout 900"
SECURITY_HEADERS_BASE="Header always set X-Frame-Options \"SAMEORIGIN\"\n  Header always set X-Content-Type-Options \"nosniff\"\n  Header always set Referrer-Policy \"no-referrer-when-downgrade\""
HSTS="Header always set Strict-Transport-Security \"max-age=63072000; includeSubDomains; preload\""
SECURITY_HEADERS_TLS="${SECURITY_HEADERS_BASE}\n  ${HSTS}"

if [[ "$MODE" == "domain" ]]; then
  if [[ "$ROUTING" == "subdomains" ]]; then
    for entry in "console 3000" "api 8080" "control 8001"; do
      sub=${entry%% *}
      port=${entry##* }
      VHOST_NAME="aion-${sub}.${DOMAIN//./-}"
      cat <<CONF >"$SITES_AVAILABLE/${VHOST_NAME}.conf"
<VirtualHost *:80${USE_IPV6:+ [::]:80}>
  ServerName ${sub}.${DOMAIN}
  ServerAdmin ${EMAIL}
  ${PROXY_TIMEOUT}
  ProxyPreserveHost On
  ProxyPass / http://127.0.0.1:${port}/ retry=0
  ProxyPassReverse / http://127.0.0.1:${port}/
  ProxyPassMatch "^/(ws|socket|stream)/?(.*)$" "ws://127.0.0.1:${port}/\$1/\$2"
  RewriteEngine On
  RewriteCond %{REQUEST_URI} !^/\.well-known/acme-challenge/
  RewriteRule ^/(.*)$ https://%{HTTP_HOST}/\$1 [R=302,L]
  ${SECURITY_HEADERS_BASE}
</VirtualHost>
CONF
      a2ensite "${VHOST_NAME}.conf" >/dev/null
    done
    certbot --apache --non-interactive --agree-tos -m "$EMAIL" \
      -d "console.${DOMAIN}" -d "api.${DOMAIN}" -d "control.${DOMAIN}"
  else
    VHOST_NAME="aion-${DOMAIN//./-}"
    cat <<CONF >"$SITES_AVAILABLE/${VHOST_NAME}.conf"
<VirtualHost *:80${USE_IPV6:+ [::]:80}>
  ServerName ${DOMAIN}
  ServerAdmin ${EMAIL}
  ${PROXY_TIMEOUT}
  ProxyPreserveHost On
  RewriteEngine On
  RewriteCond %{REQUEST_URI} !^/\.well-known/acme-challenge/
  RewriteRule ^/(.*)$ https://%{HTTP_HOST}/\$1 [R=302,L]
  ${SECURITY_HEADERS_BASE}
</VirtualHost>
CONF
    cat <<CONF >"$SITES_AVAILABLE/${VHOST_NAME}-ssl.conf"
<IfModule mod_ssl.c>
<VirtualHost *:443${USE_IPV6:+ [::]:443}>
  ServerName ${DOMAIN}
  ServerAdmin ${EMAIL}
  ${PROXY_TIMEOUT}
  ProxyPreserveHost On
  SSLEngine On
  SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
  Header always set Content-Security-Policy "default-src 'self' 'unsafe-inline'"
  ${SECURITY_HEADERS_TLS}

  ProxyPassMatch "^/(ws|socket|stream)/?(.*)$" "ws://127.0.0.1:8080/\$1/\$2"

  ProxyPass /api http://127.0.0.1:8080/api
  ProxyPassReverse /api http://127.0.0.1:8080/api

  ProxyPass /control http://127.0.0.1:8001/
  ProxyPassReverse /control http://127.0.0.1:8001/

  ProxyPass / http://127.0.0.1:3000/
  ProxyPassReverse / http://127.0.0.1:3000/
</VirtualHost>
</IfModule>
CONF
    a2ensite "${VHOST_NAME}.conf" >/dev/null
    a2ensite "${VHOST_NAME}-ssl.conf" >/dev/null
    certbot --apache --non-interactive --agree-tos -m "$EMAIL" -d "$DOMAIN"
  fi
else
  read -rp "Bind console proxy port [8088]: " CONSOLE_PORT
  CONSOLE_PORT=${CONSOLE_PORT:-8088}
  read -rp "Bind gateway proxy port [8089]: " GATEWAY_PORT
  GATEWAY_PORT=${GATEWAY_PORT:-8089}
  read -rp "Bind control proxy port [8090]: " CONTROL_PORT
  CONTROL_PORT=${CONTROL_PORT:-8090}

  cat <<CONF >"$SITES_AVAILABLE/aion-local-console.conf"
Listen ${CONSOLE_PORT}
<VirtualHost *:${CONSOLE_PORT}>
  ServerName console.local
  ${PROXY_TIMEOUT}
  ProxyPreserveHost On
  ProxyPass / http://127.0.0.1:3000/
  ProxyPassReverse / http://127.0.0.1:3000/
  ProxyPassMatch "^/(ws|socket|stream)/?(.*)$" "ws://127.0.0.1:3000/\$1/\$2"
  ${SECURITY_HEADERS_BASE}
</VirtualHost>
CONF
  cat <<CONF >"$SITES_AVAILABLE/aion-local-gateway.conf"
Listen ${GATEWAY_PORT}
<VirtualHost *:${GATEWAY_PORT}>
  ServerName api.local
  ${PROXY_TIMEOUT}
  ProxyPreserveHost On
  ProxyPass / http://127.0.0.1:8080/
  ProxyPassReverse / http://127.0.0.1:8080/
  ProxyPassMatch "^/(ws|socket|stream)/?(.*)$" "ws://127.0.0.1:8080/\$1/\$2"
  ${SECURITY_HEADERS_BASE}
</VirtualHost>
CONF
  cat <<CONF >"$SITES_AVAILABLE/aion-local-control.conf"
Listen ${CONTROL_PORT}
<VirtualHost *:${CONTROL_PORT}>
  ServerName control.local
  ${PROXY_TIMEOUT}
  ProxyPreserveHost On
  ProxyPass / http://127.0.0.1:8001/
  ProxyPassReverse / http://127.0.0.1:8001/
  ProxyPassMatch "^/(ws|socket|stream)/?(.*)$" "ws://127.0.0.1:8001/\$1/\$2"
  ${SECURITY_HEADERS_BASE}
</VirtualHost>
CONF
  for site in aion-local-console aion-local-gateway aion-local-control; do
    a2ensite "$site.conf" >/dev/null
  done
fi

systemctl reload apache2

echo "\n[SUMMARY]"
if [[ "$MODE" == "domain" ]]; then
  if [[ "$ROUTING" == "subdomains" ]]; then
    echo "- Console: https://console.${DOMAIN}"
    echo "- Gateway: https://api.${DOMAIN}"
    echo "- Control: https://control.${DOMAIN}"
  else
    echo "- Console: https://${DOMAIN}/"
    echo "- Gateway: https://${DOMAIN}/api"
    echo "- Control: https://${DOMAIN}/control"
  fi
  echo "- HSTS: max-age=63072000 (preload)"
  echo "Certificates managed by Let's Encrypt (auto-renew)."
else
  echo "- Console proxy: http://127.0.0.1:${CONSOLE_PORT}"
  echo "- Gateway proxy: http://127.0.0.1:${GATEWAY_PORT}"
  echo "- Control proxy: http://127.0.0.1:${CONTROL_PORT}"
fi

echo "Apache modules enabled: proxy, proxy_http, proxy_wstunnel, headers, ssl, http2, rewrite"
echo "Installer complete."
