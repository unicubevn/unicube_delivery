docker container prune -f
docker image prune -f
docker build -t registry.unicube.vn/unicube_delivery_stag .
docker login registry.unicube.vn -u unicube -p Unicube1511@
docker image push  registry.unicube.vn/unicube_delivery_stag:latest
