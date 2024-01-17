build_base:
	sudo docker build --progress=plain -t mverissi/root_base:v6.31.01 --compress .
build_sif:	
	make build_base	
	sudo singularity build base_conda.sif docker-daemon://mverissi/root_base:v6.31.01
push:
	sudo docker push mverissi/root_base:v6.31.01
pull:
	sudo singularity pull docker://mverissi/root_base:v6.31.01
clean:
	docker system prune
