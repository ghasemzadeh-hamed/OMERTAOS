# سناریوی استقرار Headless برای محیط تیم/CI

این راهنما یک فرآیند کاملاً خط فرمانی برای استقرار بسته‌های OMERTAOS در محیط‌های یونیکسی (بدون واسط کاربری گرافیکی) را توضیح می‌دهد. سناریوی زیر برای تیم‌ها و خطوط CI طراحی شده و تمام مراحل از آماده‌سازی سرور تا سلامت‌سنجی و رول‌بک را پوشش می‌دهد.

> **نکته**: مقادیر ارائه‌شده نمونه هستند. آن‌ها را با تنظیمات، مسیرها و آدرس‌های متناسب با زیرساخت خود جایگزین کنید.

---

## 0) پیش‌نیازها (Ubuntu/Debian یا معادل)

```bash
sudo apt-get update
sudo apt-get install -y curl git unzip tar jq ca-certificates
sudo apt-get install -y python3 python3-venv python3-pip
# در صورت نیاز: Node.js برای ابزارهای جانبی
# sudo apt-get install -y nodejs npm
# دیتابیس/کش محلی در صورت نبود سرویس خارجی
sudo apt-get install -y postgresql redis
```

## 1) کاربر و مسیرها

```bash
sudo useradd -m -s /bin/bash aion || true
sudo mkdir -p /opt/aionos /var/lib/aionos /var/log/aionos /etc/aionos/{config,keys}
sudo chown -R aion:aion /opt/aionos /var/lib/aionos /var/log/aionos /etc/aionos
```

## 2) نصب CLI (بدون UI)

فرض می‌کنیم یک باینری یا بستهٔ قابل نصب برای `aion` دارید.

```bash
curl -L "https://<artifact-host>/aion/latest/linux-x64/aion" -o /usr/local/bin/aion
sudo chmod +x /usr/local/bin/aion
# یا اگر CLI پایتونی است: یک virtualenv در /opt/aionos/cli بسازید
```

```bash
aion --version
```

## 3) ساختار باندل پیکربندی

باندل باید یک فایل `tar.gz` با ساختار مشخص باشد. نمونهٔ پیشنهادی:

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

## 4) اعمال باندل روی سرور

### انتقال باندل و آماده‌سازی متغیرهای محیطی

```bash
scp my-config.tgz user@server:/tmp/

sudo -iu aion bash -lc '
  mkdir -p ~/deploy && cp /tmp/my-config.tgz ~/deploy/
  cd ~/deploy && tar xzf my-config.tgz
  cp my-config/env/aion.env.example ~/.aion.env
  # فایل ~/.aion.env را با secrets واقعی به‌روزرسانی کنید
'
```

### اجرای `aion apply` به صورت Headless

```bash
sudo -iu aion bash -lc '
  export $(grep -v "^#" ~/.aion.env | xargs -d "\n" -n1)
  aion apply --bundle ~/deploy/my-config.tgz --no-browser
'
```

گزینهٔ `--no-browser` تضمین می‌کند فرمان کاملاً غیرتعاملی است و برای CI مناسب خواهد بود.

## 5) نصب سرویس‌ها با systemd

اگر یونیت‌های systemd داخل باندل هستند، `aion apply` می‌تواند آن‌ها را کپی و فعال کند. در غیر این صورت:

```bash
sudo cp /home/aion/deploy/my-config/services/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aion-control aion-gateway aion-console
sudo systemctl start  aion-control aion-gateway aion-console
```

نمونهٔ یونیت `aion-control.service`:

```ini
[Unit]
Description=AION Control (FastAPI)
After=network.target postgresql.service redis.service

[Service]
User=aion
EnvironmentFile=/home/aion/.aion.env
WorkingDirectory=/opt/aionos/control
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
Restart=always
RestartSec=3
StandardOutput=append:/var/log/aionos/control.log
StandardError=append:/var/log/aionos/control.err

[Install]
WantedBy=multi-user.target
```

## 6) سلامت‌سنجی و خودکارسازی CI

```bash
sudo -iu aion aion doctor --verbose
curl -s http://127.0.0.1:8001/api/health | jq .
curl -s http://127.0.0.1:8001/api/providers | jq '.items[].name'
```

هر خطایی در فرمان‌ها با کد خروج غیر صفر اعلام می‌شود و برای شکست خوردن CI کافی است.

## 7) مدیریت پروفایل‌های اجرا (CPU/GPU)

```bash
nvidia-smi || true
sudo -iu aion aion provider set-profile --name ollama-local --profile cpu
sudo -iu aion aion provider set-profile --name vllm-gpu --profile gpu
```

## 8) به‌روزرسانی و رول‌بک

```bash
scp my-config-v2.tgz user@server:/tmp/

sudo -iu aion aion apply --bundle /tmp/my-config-v2.tgz --atomic
sudo -iu aion aion rollback --last
sudo -iu aion aion module rollback summarize-rs --to 0.3.1
sudo -iu aion aion router policy-rollback --rev 17
```

## 9) نکات امنیتی و CI/CD

- Secrets را صرفاً از طریق فایل‌های ENV یا Secrets Manager تزریق کنید.
- `aion apply` باید idempotent بماند؛ اجرای تکراری نتیجهٔ مشابه بدهد.
- لاگ‌ها را در `/var/log/aionos` نگه دارید و با `journalctl -u aion-* -f` پایش کنید.
- پس از هر استقرار در CI، ترکیب `aion apply` + `aion doctor` بهترین گیت سلامت است.

## 10) چک‌لیست خلاصه

1. نصب CLI و ساخت کاربر `aion`
2. انتقال باندل و مقداردهی env
3. اجرای `aion apply --bundle … --no-browser`
4. فعال‌سازی سرویس‌های systemd
5. اجرای سلامت‌سنجی‌ها
6. پایش لاگ‌ها و آماده بودن برای رول‌بک

---

برای نمونهٔ عملی یک باندل حداقلی می‌توانید به مسیر [`deploy/headless-bundle`](../../deploy/headless-bundle) مراجعه کنید که تمام فایل‌های لازم را در قالب ساختار استاندارد فراهم کرده است.

اگر نیاز دارید پس از اعمال باندل، پیکربندی را به شکل تعاملی (اکسپلورر + چت‌بات) ادامه دهید، راهنمای [اکسپلورر متنی](./terminal-explorer.md) سه گزینهٔ مبتنی بر ترمینال (Textual، مرورگر متنی و حالت کیوسک) را پوشش می‌دهد.
