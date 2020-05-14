# zbaseball-client
A python client for the [zBaseballData](https://www.zbaseballdata.com/) API

### Note
This is a simple client and still being developed. It might have bugs, and we don't have a lot of tests. This will change. 

### Getting Started
1. Create a free account @ [zBaseballData](https://www.zbaseballdata.com/) & confirm your email
2. Install the Python Client
```bash
pip install zbaseballdata
```
3. Initialize a client
```python
from zbaseball.client import ZBaseballDataClient

# Supply the credentials you used during the sign-up process
client = ZBaseballDataClient(username="USERNAME", password="PASSWORD")
```
4. Begin Pulling Data
```python
from pprint import pprint
players = list(client.get_players(search='jeter'))
pprint(players)

"""
[{'retro_id': 'jeted001',
  'first_name': 'Derek',
  'last_name': 'Jeter',
  'debut': datetime.date(1995, 5, 29),
  'throw': 'R',
  'bat': 'R'},
 {'retro_id': 'jetej101',
  'first_name': 'Johnny',
  'last_name': 'Jeter',
  'debut': datetime.date(1969, 6, 14),
  'throw': 'R',
  'bat': 'R'},
 {'retro_id': 'jetes001',
  'first_name': 'Shawn',
  'last_name': 'Jeter',
  'debut': datetime.date(1992, 6, 13),
  'throw': 'R',
  'bat': 'L'}]
"""
```
