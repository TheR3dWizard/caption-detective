# caption-detective

Forgot Elasticsearch Password?
```sh
docker exec -it ${elasticsearch-container-name} /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

Need new enrollment token?
```sh
docker exec -it ${elasticsearch-container-name} /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
```

Need certificate to connect to your elasticsearch node?
```sh
docker cp ${elasticsearch-container-name}:/usr/share/elasticsearch/config/certs/http_ca.crt . # copies certificate to current working directory
```