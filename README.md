# MongoTV auto-download

This script checks MongoTV YouTube page every xx minutes for new videos and auto-download them to archive.

## Configuration
Go to Google console and enable youtube.googleapis.com v3 api.
Generate a API key and set in in your .env file:

https://console.cloud.google.com/apis/api/youtube.googleapis.com/
```bash
echo "API_KEY = 'API_KEY_FROM_CONSOLE'" > .env 
```



Setup a virtual environment and install dependencies

```bash
python3 -m venv venv/
source venv/bin/activate
python3 install -r requirements.txt
```

## Usage

```bash
python3 mongo.py
```