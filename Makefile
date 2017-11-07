.PHONY: docker-build docker-create install

docker-build:
	docker build --tag hashweb:latest .

docker-create:
	docker create --tty --interactive \
    --name hashweb \
    --hostname hashweb \
    --volume ${PWD}/../:/home/developer/workspace \
    --publish 8080:8080 \
    hashweb

install:
	pip3 install -r requirements.txt
	wget http://logs.hashweb.org/dev/hashweb_all.gz
	sudo -u developer memcached -d -s /tmp/memcached.sock
	gunzip -c hashweb_all.gz > hashweb_all.sql
	service postgresql start
	sudo -u postgres psql -f hashweb_all.sql postgres
	rm hashweb_all.sql hashweb_all.gz

docker-sandbox: docker-build docker-create
