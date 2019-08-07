**How to run**

Docker engine and docker-compose is required to run this properly. I'm assuming both of them are installed on the
machine.


Inside the `docker_mondis` directory run the docker-compose up command

    docker-compose up --build -d

The `-d` argument can be omitted for not running it as a daemon, or if you can run

    docker-compose logs --tail=0 -f

to view the latest logs.

This will create a Django application inside the docker container and it will run on `0.0.0.0:8011`

Now it can be tested using the `curl` command or from the browser


**Running sample tests**

    docker exec -it mondis-django python manage.py test
