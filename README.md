# Tsuki
Tsuki is a minimalistic open-sourced social media platform, built using Python.

> **Note**
> Tsuki also has a Golang version, https://github.com/Devansh3712/tsuki-go

## Running on local machine

### Requirements
- Tsuki requires a `PostgreSQL` database to store all the data.
- It uses the `Gmail API` for sending verification mail ([Reference](https://developers.google.com/gmail/api/quickstart/python)) and the `Freeimage API` for storing pictures ([Reference](https://freeimage.host/page/api)).
- It also requires some environment variables to be declared in the `.env` file. The variables can be found in `example.env`

### Installation
The installation can be done either using `pip` or `poetry`.

Using `pip`,
```console
pip install requirements.txt
```

Using `poetry`,
```console
poetry install
```

> **Note**
> If `poetry` is used for installation, please install `scikit-learn` using `pip` as it gave dependency issues.
> ```console
> pip install scikit-learn
> ```

### Run

```console
uvicorn tsuki.main:app
```
