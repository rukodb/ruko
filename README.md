# Ruko

*A simple-to-use, in-memory JSON database*

Many small to medium sized database applications require the use of a database for
persistent storage of a small amount of data (up to a few gigabytes). While tools like
Redis provide simple O(1) key value stores, larger applications easily become
overly complicated due to the flat nature of key value stores along with JSON being a second
class citizen. Ruko aims to solve this problem by being a fast, in-memory JSON database
where all requests are O(1) (or O(n) if it has to build an index). Learn more about it below.

## Usage

Start ruko server process:
```bash
ruko-server
```

Example Python code:
```python
from ruko import RDict

db = RDict.client()
notes = db['notes']

def get_notes():
    return notes.get()

def create_note(title, note):
    notes.append({
        'title': title,
        'note': note
    })
    return notes[-1]()

def get_note_by_title(title):
    return notes.by('title')[title]()
```

If you are using [Flask](http://flask.pocoo.org/), checkout [Flask-Ruko](https://github.com/rukodb/flask-ruko).

### Details

#### Requests

Ruko consists of a json database backend and a native feeling Python
interface. Requests consist of a key location and a request type. Requests
are only performed via one of the following:
 - `.get()`: This immediately performs a request, returning the default value or `None` as expected in Python
 - `()`: Calling an index performs the request
 - `.append()`, `.keys()`, `len(x)`, `y in x`, etc. Performing an operation on an  `RDict` performs a request
 - `['key'] = ...` Item assignment performs a request
 
 For example, each of these lines performs one request:
 
  - `db['users']['abc'].get('name', 'john')`
  - `abc_user = db['users']['abc']()`
  - `db['users']['abc']['devices'].append({'name': 'def'})`
  - `db['users']['abc'] = {'devices': {'name': 'def'}}`

**Difference between `.get()` and `()`:**

When using `.get`, it returns a default value if no vaue is present. `()`, however,
raises `KeyError` (or the default error class) if the value is not present.

#### Get by

Additionally, you can search for a value inside a list or a dictionary based on its attributes:

```python
users = db['users']
users[()] = [
    {'name': 'John', 'email': 'john325@gmail.com'},
    {'name': 'Sam', 'email': 'sam151@yahoo.com'},
    {'name': 'Kelly', 'email': 'kelly12@gmail.com'}
]  # Assign the current object via [()] = ...

users.by('name')['Sam']()  # {'name': 'Sam', 'email': 'sam151@yahoo.com'}
```
 
 #### Mappings
Sometimes various objects that reside in different locations need to be
aggregated and searched. This is where mappings come into play. For
example:

 ```python
users = db['users']
users.append({
    'name': 'John',
    'email': 'john325@gmail.com',
    'devices': [
        {'id': 'abc', 'name': "John's first device"},
        {'id': 'def', 'name': "John's second device"}
    ]
})
users.append({
    'name': 'Sam',
    'email': 'sam151@yahoo.com',
    'devices': [
        {'id': 'ghi', 'name': "Sam's first device"},
        {'id': 'jkl', 'name': "Sam's second device"}
    ]
})
devices = db.create_mapping('devices', 'users.*.devices.*')

devices.by('id')['ghi'].get()  # {'id': 'ghi', 'name': "Sam's first device"}
```

## Installation

 - Compile and install [ruko-server](https://github.com/rukodb/ruko-server)
 - Install the `ruko` python package:
 
 ```bash
 pip install ruko
 ```

## Contributing

Ruko is in active development and encourages contributions from anyone.
