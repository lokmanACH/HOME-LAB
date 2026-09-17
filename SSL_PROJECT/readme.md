# 🔐 Nginx + OpenSSL HTTPS Lab

A small **Home Lab / DevOps project** to understand how **Nginx, OpenSSL, SSL/TLS certificates, and reverse proxying** work together.

The goal of this project is not to build a production-ready HTTPS setup, but to experiment with the fundamentals and understand what happens behind the scenes.

---

## 📌 What I Built

In this mini project, I:

* Installed **Nginx**
* Installed **OpenSSL**
* Generated a **private key**
* Generated a **self-signed SSL/TLS certificate**
* Configured **Nginx to use HTTPS**
* Used Nginx as a **reverse proxy**
* Tested the HTTPS connection using `curl`
* Troubleshot a TLS/certificate error
* Learned the difference between **HTTP, HTTPS, certificates, and certificate trust**

The final architecture looks like this:

```text
                    HTTPS
                     │
                     ▼
              ┌──────────────┐
              │    Nginx     │
              │              │
              │ SSL/TLS      │
              │ Termination  │
              └──────┬───────┘
                     │
                  HTTP
                     │
                     ▼
              ┌──────────────┐
              │ Test Service │
              │    :3100     │
              └──────────────┘
```

---

# 🧰 Technologies

* Linux / Ubuntu
* Nginx
* OpenSSL
* Bash
* curl
* HTTP / HTTPS
* SSL/TLS
* Reverse Proxy

---

# 📂 Project Structure

```text
.
├── guide.sh
└── README.md
```

The `guide.sh` script contains the commands used to build the lab step by step.

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_PROJECT_DIRECTORY>
```

---

## 2. Run the guide

Make the script executable:

```bash
chmod +x guide.sh
```

Run it:

```bash
./guide.sh
```

The script installs the required software and prepares the SSL directory.

---

# 📦 1. Install Nginx and OpenSSL

The first step is installing the required packages:

```bash
sudo apt update
sudo apt install nginx openssl -y
```

Then check the installed versions:

```bash
openssl version
nginx -v
```

This is useful for verifying that both tools are installed correctly.

---

# ⚙️ 2. Start Nginx

The script starts Nginx:

```bash
sudo systemctl start nginx
```

And enables it to start automatically when the machine boots:

```bash
sudo systemctl enable nginx
```

You can verify its status with:

```bash
sudo systemctl status nginx
```

---

# 🔑 3. Create the SSL Directory

We create a dedicated directory for the Nginx SSL files:

```bash
sudo mkdir -p /etc/nginx/ssl
```

The directory will contain:

```text
/etc/nginx/ssl/
├── nginx.key
└── nginx.crt
```

---

# 🔐 4. Generate the Private Key

We generate a 2048-bit RSA private key:

```bash
sudo openssl genrsa \
    -out /etc/nginx/ssl/nginx.key \
    2048
```

The private key is then protected:

```bash
sudo chmod 600 /etc/nginx/ssl/nginx.key
```

### Why?

The private key is sensitive.

It should not be readable by normal users or exposed publicly.

```text
nginx.key
   │
   └── 🔒 PRIVATE
```

---

# 📜 5. Generate a Self-Signed Certificate

The certificate is generated using OpenSSL:

```bash
sudo openssl req -x509 \
    -new \
    -key /etc/nginx/ssl/nginx.key \
    -sha256 \
    -days 365 \
    -out /etc/nginx/ssl/nginx.crt
```

This creates:

```text
nginx.crt
```

The certificate is valid for **365 days**.

Because we generated it ourselves, it is called a:

> **Self-signed certificate**

It is useful for learning and testing, but browsers and operating systems generally do not automatically trust it like a certificate issued by a public Certificate Authority.

---

# 🌐 6. Configure Nginx

Nginx needs to be configured to listen for HTTPS traffic.

Example:

```nginx
server {
    listen 5050 ssl;
    server_name localhost;

    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;

    location / {
        proxy_pass http://127.0.0.1:3100;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

The important part is:

```nginx
listen 5050 ssl;
```

The `ssl` tells Nginx that this listener should use TLS.

Then we tell Nginx where the certificate and private key are:

```nginx
ssl_certificate /etc/nginx/ssl/nginx.crt;
ssl_certificate_key /etc/nginx/ssl/nginx.key;
```

---

# 🔄 7. Nginx as a Reverse Proxy

The request flow is:

```text
Client
  │
  │ HTTPS :5050
  ▼
Nginx
  │
  │ TLS termination
  │
  │ HTTP
  ▼
Test Service :3100
```

Nginx receives the HTTPS request and handles the TLS encryption.

Then it forwards the request to the backend service using:

```nginx
proxy_pass http://127.0.0.1:3100;
```

This is called **TLS termination**.

---

# 🧪 8. Test the HTTP Service

Before enabling HTTPS, the backend can be tested directly:

```bash
curl http://localhost:3100
```

Example response:

```text
Hello World!
```

---

# 🔒 9. Test HTTPS

After configuring Nginx:

```bash
curl https://localhost:5050
```

Because the certificate is self-signed, `curl` may reject it because it does not trust the certificate.

For testing, you can bypass certificate verification:

```bash
curl -k https://localhost:5050
```

Expected result:

```text
Hello World!
```

### What does `-k` mean?

`-k` means:

```text
--insecure
```

It tells curl not to verify the certificate's trust chain.

This is useful for a lab, but **should not be used as a solution for production certificate validation**.

---

# 🐛 Troubleshooting

During the lab, I encountered:

```text
curl: (35) TLS connect error:
SSL routines::wrong version number
```

This happened because Nginx was configured with:

```nginx
listen 5050;
```

instead of:

```nginx
listen 5050 ssl;
```

The certificate paths alone are not enough.

Nginx must also enable SSL/TLS on the listener.

---

## Certificate Validation

Another error can look like:

```text
curl: (60) SSL:
unable to obtain common name from peer certificate
```

This can happen when the certificate does not contain the correct hostname in its **Subject Alternative Name (SAN)**.

For example, a certificate intended for:

```text
localhost
```

should contain something like:

```text
DNS:localhost
```

Modern TLS clients rely on SAN for hostname verification.

---

# 🔎 Inspect the Certificate

You can inspect the certificate using:

```bash
openssl x509 \
    -in /etc/nginx/ssl/nginx.crt \
    -text \
    -noout
```

You can also check the certificate dates:

```bash
openssl x509 \
    -in /etc/nginx/ssl/nginx.crt \
    -noout \
    -dates
```

And check the subject:

```bash
openssl x509 \
    -in /etc/nginx/ssl/nginx.crt \
    -noout \
    -subject
```

---

# 🧠 What I Learned

This lab helped me understand several important concepts:

### HTTP

```text
Client ────────────────> Server
        HTTP
```

The communication is not encrypted.

### HTTPS

```text
Client ────────────────> Nginx
          HTTPS/TLS
```

TLS provides encryption and server authentication through certificates.

### Private Key

```text
nginx.key
```

Used by the server as part of the TLS process.

It must remain private.

### Certificate

```text
nginx.crt
```

Contains information about the server identity and is used during TLS authentication.

### Self-Signed Certificate

A certificate signed by itself rather than by a trusted public Certificate Authority.

Good for:

* Home labs
* Local development
* Learning
* Testing

Not appropriate by itself for a typical public production website.

---

# 🔮 Possible Next Steps

This mini project can be extended with:

* [ ] Create a proper certificate with **SAN**
* [ ] Create a local Certificate Authority
* [ ] Configure Nginx with multiple HTTPS services
* [ ] Redirect HTTP → HTTPS
* [ ] Add TLS security settings
* [ ] Add Docker containers behind Nginx
* [ ] Add Nginx load balancing
* [ ] Use Let's Encrypt
* [ ] Use a real domain
* [ ] Add monitoring with Prometheus and Grafana
* [ ] Add Nginx access/error logs monitoring

---

# 🎯 Goal of the Lab

The main goal is to understand the basic infrastructure behind:

```text
                 Internet
                    │
                 HTTPS
                    │
                    ▼
              ┌───────────┐
              │   Nginx   │
              │ SSL/TLS   │
              └─────┬─────┘
                    │
              Reverse Proxy
                    │
                    ▼
             ┌────────────┐
             │  Backend   │
             │  Service   │
             └────────────┘
```

This is a small **Home Lab experiment** focused on learning and hands-on practice with Linux, networking, DevOps, and web infrastructure.
