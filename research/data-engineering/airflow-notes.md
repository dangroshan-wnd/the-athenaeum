### General commands ###

- See what containers are running: `docker ps`
    - Inside: try `ls /opt/python`, `cat /opt/python/tickers.json`
    - To exit: `exit`

### Rebuild Airlfow ###

- Enter the project folder in powershell, e.g.: `cd projects/raspberry-bi`
- Rebuild the image, e.g.: `docker build -t dock-raspberry-pi .`
    - Optional: force full rebuild if caching acts up, e.g.: `docker build --no-cache -t dock-raspberry-pi .`

### Compose up/down ###

Do UP after starting the Airflow environment, making changes to docker-compose.yaml, or after rebuilding images.
Do DOWN when you want to stop all services, before making config changes or nuking volumes, or to reset the environment.

- `docker-compose up -d --build`
- `docker-compose down`
- `docker-compose down --volumes` to nuke volumes

### Enter a Container in Terminal ###

- Using powershell, from the project folder e.g. projects/raspberry-bi/, do: `docker exec -it raspberry-pi-airflow-webserver-1 /bin/bash`
- Check versions:
    - pip show apache-airflow
    - pip show apache-airflow-providers-docker
