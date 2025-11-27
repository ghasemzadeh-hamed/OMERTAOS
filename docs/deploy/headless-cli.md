#   Headless   /CI

          OMERTAOS    (   )   .       CI               .

> ****:    .             .

---

## 0)  (Ubuntu/Debian  )

```bash
sudo apt-get update
sudo apt-get install -y curl git unzip tar jq ca-certificates
sudo apt-get install -y python3 python3-venv python3-pip
#   : Node.js
# sudo apt-get install -y nodejs npm
# /
sudo apt-get install -y postgresql redis
```

## 1)

```bash
sudo useradd -m -s /bin/bash aion || true
sudo mkdir -p /opt/aionos /var/lib/aionos /var/log/aionos /etc/aionos/{config,keys}
sudo chown -R aion:aion /opt/aionos /var/lib/aionos /var/log/aionos /etc/aionos
```

## 2)  CLI ( UI)

         `aion` .

```bash
curl -L "https://<artifact-host>/aion/latest/linux-x64/aion" -o /usr/local/bin/aion
sudo chmod +x /usr/local/bin/aion
#   CLI  :  virtualenv  /opt/aionos/cli
```

```bash
aion --version
```

## 3)

    `tar.gz`    .  :

```
my-config/
  config/
    providers.yaml
    router.policy.yaml
    data-sources.yaml
  modules/
    summarize-rs/
      aip.yaml
      cosign.pub
    ocr-py/
      aip.yaml
  services/
    aion-control.service
    aion-gateway.service
    aion-console.service
  env/
    aion.env.example
  scripts/
    pre-apply.sh
    post-apply.sh
    verify.sh
  VERSION
  CHECKSUMS.txt
```

## 4)

###

```bash
scp my-config.tgz user@server:/tmp/

sudo -iu aion bash -lc '
  mkdir -p ~/deploy && cp /tmp/my-config.tgz ~/deploy/
  cd ~/deploy && tar xzf my-config.tgz
  cp my-config/env/aion.env.example ~/.aion.env
  #  ~/.aion.env   secrets
'
```

###  `aion apply`   Headless

```bash
sudo -iu aion bash -lc '
  export $(grep -v "^#" ~/.aion.env | xargs -d "\n" -n1)
  aion apply --bundle ~/deploy/my-config.tgz --no-browser
'
```

 `--no-browser`         CI   .

## 5)    systemd

  systemd    `aion apply`       .    :

```bash
sudo cp /home/aion/deploy/my-config/services/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aion-control aion-gateway aion-console
sudo systemctl start  aion-control aion-gateway aion-console
```

  `aion-control.service`:

```ini
[Unit]
Description=AION Control (FastAPI)
After=network.target postgresql.service redis.service

[Service]
User=aion
EnvironmentFile=/home/aion/.aion.env
WorkingDirectory=/opt/aionos/control
ExecStart=/usr/bin/python3 -m uvicorn os.control.main:app --host 0.0.0.0 --port 8001 --workers 4
Restart=always
RestartSec=3
StandardOutput=append:/var/log/aionos/control.log
StandardError=append:/var/log/aionos/control.err

[Install]
WantedBy=multi-user.target
```

## 6)    CI

```bash
sudo -iu aion aion doctor --verbose
curl -s http://127.0.0.1:8001/api/health | jq .
curl -s http://127.0.0.1:8001/api/providers | jq '.items[].name'
```

               CI  .

## 7)    (CPU/GPU)

```bash
nvidia-smi || true
sudo -iu aion aion provider set-profile --name ollama-local --profile cpu
sudo -iu aion aion provider set-profile --name vllm-gpu --profile gpu
```

## 8)

```bash
scp my-config-v2.tgz user@server:/tmp/

sudo -iu aion aion apply --bundle /tmp/my-config-v2.tgz --atomic
sudo -iu aion aion rollback --last
sudo -iu aion aion module rollback summarize-rs --to 0.3.1
sudo -iu aion aion router policy-rollback --rev 17
```

## 9)    CI/CD

- Secrets      ENV  Secrets Manager  .
- `aion apply`  idempotent      .
-    `/var/log/aionos`     `journalctl -u aion-* -f`  .
-      CI  `aion apply` + `aion doctor`    .

## 10)

1.  CLI    `aion`
2.     env
3.  `aion apply --bundle ... --no-browser`
4.   systemd
5.
6.

---

         [`deploy/headless-bundle`](../../deploy/headless-bundle)              .

            ( + )    [ ](./terminal-explorer.md)      (Textual     )   .
