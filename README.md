# github-issue-tracker
A GitHub issue tracker to follow GitHub issues with django and drf

## Technology Stack
This is a list of mostly used technologies and libraries that are used in project:

- [Python](https://www.python.org/) is an interpreted high-level programming language for general-purpose programming.

- [Django](https://www.djangoproject.com/) is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.

- [Django Rest Framework](https://www.django-rest-framework.org/) is a powerful and flexible toolkit for building Web APIs.

- [PostgreSQL](https://www.postgresql.org) is a free and open-source relational database management system emphasizing extensibility and SQL compliance.

- [Redis](https://redis.io) is an open source, in-memory data structure store, used as a database, cache, and message broker

- [Docker](https://www.docker.com) is an application build and deployment tool. It is based on the idea of that you can package your code with dependencies into a deployable unit called a container.

- [Celery](https://docs.celeryproject.org/en/stable/) is an asynchronous task queue/job queue based on distributed message passing.

- [MailHog](https://github.com/mailhog/MailHog?tab=readme-ov-file) is an email testing tool for developers.


## Installation
This project are used docker to run the project, [download docker here](https://www.docker.com/community-edition) if you haven't done so.
Docker can't help for some devices. If the project does not work with Docker, [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/#step-2-install-docker-toolbox) will help you.

In order to easy the use of Docker commands, the project has a Makefile that encapsulates the commands you'll need.

Before running the project, create your own environment file (`.env`). Simply run the following command, and edit the variables:
```shell
cp .env.sample .env
```

### GitHub API Token
To use the GitHub API, you need to create a GitHub API token. You can create a token by following the steps below:
1. Go to your GitHub account settings.
2. Click on Developer settings.
3. Click on Personal access tokens.
4. Click on Tokens (classic).
5. Click on Generate new token.
6. Give a name to the token and select the scopes you need.
(In actually you don't need any scope on this project because public repositories are accessible without permissions. But if you want to access private repositories, you need to select the appropriate scopes.)
7. Click on Generate token.
8. Copy the token and paste it to the `.env` file as `GITHUB_API_TOKEN`.
9. Save the `.env` file.

### Build the project
To build the project, run the following command:
```shell
make build
```

### Run the project
To run the project, run the following command:
```shell
make up
```

### Create superuser
To create a superuser, run the following command:
```shell
make createsuperuser
```
This user will be used to login to the Django admin panel and to access the API.

You can use that user to login and follow the repositories.

### Access the Django admin panel

To access the Django admin panel, go to [http://localhost:8000/admin](http://localhost:8000/admin) and login with the superuser credentials.

### Access the API

To access the API, go to [http://localhost:8000/api](http://localhost:8000/api).

You can see the list of all active API endpoints.

### Docs

To access the API documentation, go to [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/).

And also you can access the Swagger documentation by going to [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/).


#### Celery and Email
In every 1 hour, the project checks the repositories you followed and sends an email if there is an issue created or updated.

("gissues.extensions.github_client.tasks.CheckForNewIssues" task is responsible for this.)

You can change the schedule time by set the 'CHECK_FOR_NEW_ISSUES_INTERVAL_IN_MINUTES' in the `.env` file.'


Also, you can check the celery tasks by going to [http://localhost:5555](http://localhost:5555).

And you can see the emails that are sent by the project by going to [http://localhost:8025](http://localhost:8025).


### Makefile command reference

|       Command        | Explanation                                                                                                                                                                       |
|:--------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|          up          | Build the containers if not done so, then run them. The logs of all containers will be streamed while the script is running. You can terminate the script to stop the containers. |
|         down         | Stop all containers and purge all the data in them.                                                                                                                               |
|        build         | Build the containers.                                                                                                                                                             |
|       restart        | Restart the containers.                                                                                                                                                           |
|        start         | Start all containers.                                                                                                                                                             |
|         stop         | Stop all containers.                                                                                                                                                              |
|        shell         | Enter the Python shell in Django container.                                                                                                                                       |
|         test         | Run tests.                                                                                                                                                                        |
|         mypy         | Run mypy type checking.                                                                                                                                                           |
|      changelog       | Generate a changelog based on the commit messages.(requires [git-cliff](https://git-cliff.org) to be installed in local environment)                                              |
|         logs         | Stream all container logs.                                                                                                                                                        |
| compile-requirements | Compile Poetry requirements and dump it into requirements.txt (requires Poetry to be installed in local environment)                                                              |
|        django        | Run Django commands. You can add your command in order.                                                                                                                           |


## Maintainers
- Ömer Faruk Korkmaz
