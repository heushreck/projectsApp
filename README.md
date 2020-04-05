# Project Storage and Retrieve Service

## Authentication

A Authentication Token needs to be produced first

### Adding a new user
`POST /users`
An loged in Admin user can create a new users
```json
{
    "user_name": "name",
    "password": "password"
}
```
### Seeing all users
Also only an Admin can see users and manipulate them
`GET /users`
**Response**
```
[
    {
        "user_name": "Admin",
        "password": "sha256$13FgwDu0$d29a3d637177e6b3fa47f84daecffbc019a09151c7b130",
        "public_id": "4638175e-f122-b594-1cbff5dd39e7",
        "admin": true
    },
    {
        "user_name": "Nicolas",
        "password": "sha256$YRae0qf6$d56e906d1dd605dc533370194e35b2a6307805cb6e3f41678d",
        "public_id": "87e01fa8-1670840f-181b0028c967",
        "admin": false
    },
    {
        "user_name": "Thomas",
        "password": "sha256$srvm7f71140b78a4bab7f204784c17d0f7954903a591baf4258",
        "public_id": "023fa3b9-4505-ba9b-093ede9addde",
        "admin": false
    }
]
```
### Seeing one user
Admin only
`GET /users/<string:public_id>`

### Login
`GET /login`
with Basic Auth username and password you can login and will be presented with a token
Pass that token as the header:
`-H "x-access-token:<your-token>"`

## Usage

All responses will have the form

```json
{
    "data": "Mixed type holding the content of the response",
    "message": "Description of what happened"
}
```

Subsequent response definitions will only detail the expected value of the `data field`

### List all projects

**Definition**

`GET /projects`

**Response**

- `200 OK` on success

```json
[
    {
        "identifier": "todo-app",
        "name": "Todo App",
        "githup": "switch",
        "resources" : [],
        "finished": false
    },
    {
        "identifier": "torben",
        "name": "TorbenTrinkt",
        "githup": "https://github.com/heushreck/TorbenTrinkt",
        "resources" : [
          {"splashcreen":"https://www.google.com/search?q=splashcreen"}
        ],
        "finished": true
    }
]
```

### Adding new Project

**Definition**

`POST /projects`

**Arguments**

- `"identifier":string` a globally unique identifier for this project
- `"name":string` a friendly name for this project
- `"githup":string` web address of the github repo
- `"resources":array` what resources were used
- `"finished":boolean` is the project is already finished

If a project with the given identifier already exists, the existing project will be overwritten.

**Response**

- `201 Created` on success

```json
{
    "identifier": "todo-app",
    "name": "Todo App",
    "githup": "switch",
    "resources" : [],
    "finished": false
}
```

## Lookup project details

`GET /projects/<identifier>`

**Response**

- `404 Not Found` if the project does not exist
- `200 OK` on success

```json
{
    "identifier": "todo-app",
    "name": "Todo App",
    "githup": "switch",
    "resources" : [],
    "finished": false
}
```

## Delete a project

**Definition**

`DELETE /projects/<identifier>`

**Response**

- `404 Not Found` if the project does not exist
- `204 No Content` on success


## Exmaple

`curl -H "Content-Type: application/json" -X POST -d '{"identifier": "todo-app","name": "Todo App","githup": "switch","resources" : [{"abc":"def", "def":"huid"}],"finished": false}' http://localhost:5000/projects`
