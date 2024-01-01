pip freeze > requirements.txt
docker build -t heatingcontrol -f Dockerfile .
docker tag heatingcontrol:latest docker.diskstation/heatingcontrol
docker push docker.diskstation/heatingcontrol:latest