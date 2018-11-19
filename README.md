# ogem-planner

## Installation

### Configuration

`scraper.py` uses credentials from a file named `credentials.py`. In order for this to work, run the following commands:

```sh
touch credentials.py
sudo nano credentials.py
```

Paste the following inside:

```
# credentials.py

username = '<domain>\<username>'
password = '<password>'
```