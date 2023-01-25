build:
	docker build --network host --compress -t jodafons/root-cern:latest .
push:
	docker push jodafons/root-cern:latest
pull:
	singularity pull docker://jodafons/root-cern:latest