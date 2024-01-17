build_base:	
	sudo docker build --progress=plain -t mverissi/base_conda:tf --compress .
build_sif:	
	make build_base	
	sudo singularity build base_conda.sif docker-daemon://mverissi/base_conda:tf
clean:
	docker system prune -a
push:
	docker push mverissi/base_conda:tf
pull:
	singularity pull docker://mverissi/base_conda:tf
