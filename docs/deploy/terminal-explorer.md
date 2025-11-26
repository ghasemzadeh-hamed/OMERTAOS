#      (Headless)

        +        .             API  (`aion-control`)  .

> ** :**  HTTP       (`AION_TOKEN`).

---

##  A)  Textual ()

   (TUI)    [Textual](https://textual.textualize.io/)    (Providers/Modules/Data Sources)        .

### 

```bash
python3 -m pip install --upgrade textual rich requests
```

### 

```bash
python3 -m console.tui.explorer --api http://127.0.0.1:8001 --token "$AION_TOKEN"
```

### 

-   (`add provider ...`, `set router ...`, `add ds ...`, `list providers`  ...)
-    Explorer   `Ctrl+R`
- `Ctrl+D`    
-        

>   SSH              .

---

##  B)   +   (w3m/lynx)

 [`scripts/aion-explorer`](../../scripts/aion-explorer)     (FastAPI +  HTML )         (`w3m` `lynx`  `links`)      .

### 

```bash
sudo apt-get install -y w3m #  lynx/links
python3 -m pip install --upgrade fastapi uvicorn requests
```

### 

```bash
AION_API=http://127.0.0.1:8001 \
AION_TOKEN="$AION_TOKEN" \
AION_EXPLORER_PORT=3030 \
scripts/aion-explorer
```

             `http://127.0.0.1:3030/`  .               .

###   

- `AION_EXPLORER_PORT`:   ( 3030)
- `AION_EXPLORER_HOST`:    ( 127.0.0.1)
- `AION_EXPLORER_LOG`:    

    `q`   w3m/lynx        .

---

##  C)     

       VM                  App Mode /   :

```bash
AION_TOKEN="$AION_TOKEN" \
AION_EXPLORER_PORT=3030 \
AION_EXPLORER_LOG=/tmp/aion-explorer.log \
AION_EXPLORER_HOST=127.0.0.1 \
scripts/aion-explorer &

chromium --app="http://127.0.0.1:3030/?token=$AION_TOKEN" --kiosk
```

        :

```bash
python3 -m console.tui.web_server --api http://127.0.0.1:8001 --token "$AION_TOKEN"
#    : xdg-open http://127.0.0.1:3030/
```

     UI           .

---

##    

  TUI ( A)       ( B/C)      [`console/tui/api.py`](../../console/tui/api.py)  .  :

```
help
list providers|modules|datasources
add provider <name> key=... [kind=local|api] [base_url=...]
add ds <name> kind=postgres dsn=postgres://... [readonly=true]
set router policy=<default|auto> [budget=200] [failover=on|off]
reload router
test ds <name>
```

    API    ``              .

---

##    CI/CD

-             CI    (: `textual run ...`  `scripts/aion-explorer`).
-           (`AION_EXPLORER_LOG`)  .
-  idempotent                     .

---

###   

|                   |                      |                                                                |
| ---------------------- | ------------------------- | -------------------------------------------------------------------- |
| `   API: 401`   |      |  `AION_TOKEN`   .                                    |
| `   ` | w3m/lynx           |  `apt-get install w3m`      A  .        |
| UI  SSH      |   UTF-8        |  `LC_ALL`/`LANG`   `en_US.UTF-8`  `fa_IR.UTF-8` . |

---

###  

-        Headless  [ Headless](./headless-cli.md)                 .
-          `ControlAPI`  `CommandProcessor`         TUI  .
