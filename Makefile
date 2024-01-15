build:
	docker build --network host --compress -t jodafons/root-cern:v6.31.01 .
push:
	docker push jodafons/root-cern:v6.31.01
pull:
	singularity pull docker://jodafons/root-cern:v6.31.01
