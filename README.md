# Blockpass AuthBackend Service

This repo implement basic features of Blockpass [Server Spec V1](https://github.com/blockpass-org/blockpass/wiki/Server_Spec_V1)

## Use Cases

1. User Using Blockpass Mobile app (V1.1+) to scan QR code from website

2. Server side handle logic

- **User registered** (approved) by services --> SSO payload is going to send to website.[blockpass_handler.py#ssoComplete](/modules/handlers/blockpass_handler.py)

- **New user** create new record -> generate `one_time_pass` inside api `/login` and request Mobile App upload data via `/uploadData` endpoints

Example website (for QR Code scanning) can be found [/example-web](/example-web)

## Pre-configuration

- This example consumed `email`, `selfe` and `onfido certificate` (config inside `kyc_record_model.py`)

- This example using default config (`config.py`):

  - BaseUrl: [https://sandbox-api.blockpass.org](https://sandbox-api.blockpass.org)

  - ClientSecret: `developer_service`

  - ClientId: `developer_service`

- `developer_service` setting on Blockpass Developer pages as below:

``` javascript
{
    "register" : "http://192.168.1.116:3000/blockpass/api/register",
    "login" : "http://192.168.1.116:3000/blockpass/api/login",
    "upload" : "http://192.168.1.116:3000/blockpass/api/uploadData",
    "status" : "http://192.168.1.116:3000/blockpass/api/status",
}
```

Note:

- In order easy to develop we setup LAN ip for services. It allow Mobile App (connect to same LAN) send data direct to developer machine

## Features

- [x] Requirement endpoints(/status /login /register /uploadData)

- [x] Blockpass services API [Handshake](https://github.com/blockpass-org/blockpass/wiki/Server_Spec_V1#1-handshake)

- [x] Blockpass services API [Query Profile](https://github.com/blockpass-org/blockpass/wiki/Server_Spec_V1#3-query-blockpassprofile)

- [x] Blockpass services API [Single Sign On Complete](https://github.com/blockpass-org/blockpass/wiki/Server_Spec_V1#4-single-sign-on-complete)

- [ ] Blockpass services API [Refresh Token](https://github.com/blockpass-org/blockpass/wiki/Server_Spec_V1#2-refresh-accesstoken)

- [ ] Handle reject and approved fields ( request upload again)

- [ ] Certificate issues to client

## Install dependencies

```sh
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
python application.py
```

## Run using docker

```sh
docker build . -t myapp
docker run -d myapp
```

Powered by [flask-backend-boilerplate](https://github.com/anpandu/flask-backend-boilerplate)