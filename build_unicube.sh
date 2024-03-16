docker container prune -f
docker image prune -f
docker build --platform="linux/amd64" -t registry.unicube.vn/unicube_delivery_stag .
docker login  registry.unicube.vn -u unicube -p Unicube1511@
docker image push  registry.unicube.vn/unicube_delivery_stag:latest
docker builder prune -f

# --platform="linux/amd64"