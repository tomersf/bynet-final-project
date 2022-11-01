<!-- ABOUT THE PROJECT -->

## About The Project

A simple attendance project created with flask, react & mysql.
Including CI & CD Pipeline with jenkins

### Built With

- [![React][react.js]][react-url]
- [![Mysql][mysql.dev]][mysql-url]
- [![Flask][flask.dev]][flask-url]

### Prerequisites

- Docker
- Docker-compose

### Installation

1. Make sure to set env vars in a compose.env file within the docker-compose.dev.yml file directory

```sh
MYSQL_DB=exercise
MYSQL_USER=tomer
MYSQL_PASSWORD=123456
MYSQL_HOST=mysql
REMOTE_USERNAME=<remote username of the course machine>
REMOTE_PASSWORD=<your password for the course machine>

MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=exercise
```

2. Run the following command (need docker installed)
   ```sh
   docker-compose -f docker-compose.dev.yml up
   ```
3. Go to localhost:3050 and check the project, also got sorting options by the attendance duration of the students.

[mysql.dev]: https://img.shields.io/badge/Mysql-DD0031?style=for-the-badge&logo=mysql&logoColor=white
[mysql-url]: https://www.mysql.com/
[react.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[react-url]: https://reactjs.org/
[flask.dev]: https://img.shields.io/badge/Flask-563D7C?style=for-the-badge&logo=flask&logoColor=white
[flask-url]: https://flask.palletsprojects.com/en/2.2.x/

### Screenshots

![Home Screen](https://github.com/tomersf/bynet-py-app/blob/master/screenshots/indexScreen.png?raw=true)
![Loading Screen](https://github.com/tomersf/bynet-py-app/blob/master/screenshots/loadingScreen.png?raw=true)
