## Soalpich

![GitHub repo status](https://img.shields.io/badge/status-active-green?style=flat)
![GitHub license](https://img.shields.io/github/license/sheikhartin/soalpich)
![GitHub contributors](https://img.shields.io/github/contributors/sheikhartin/soalpich)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/sheikhartin/soalpich)
![GitHub repo size](https://img.shields.io/github/repo-size/sheikhartin/soalpich)

A platform for quizzes and also chatting...

### How to Use

First, install the dependencies:

```bash
poetry install
```

Configure the database and adapt the environment variables to it... Look at the example [here](soalpich/.env.example).

Apply migrations:

```bash
poetry run python manage.py makemigrations \
&& poetry run python manage.py migrate
```

Load a simple database:

```bash
poetry run python manage.py loaddata db.json
```

Test it before running:

```bash
poetry run python manage.py test
```

Run it:

```bash
poetry run python manage.py runserver --insecure
```

Don't forget to run a Redis server on the port specified in the environment variables:

```bash
redis-server --port 6347
```

Check project status for deployment:

```bash
poetry run python manage.py check --deploy
```

### License

This project is licensed under the MIT license found in the [LICENSE](LICENSE) file in the root directory of this repository.
