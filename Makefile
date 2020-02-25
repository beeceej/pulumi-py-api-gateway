.PHONY: up destroy clean all
.DEFAULT_GOAL := up

up:
	pulumi up --yes -r

destroy:
	pulumi destroy --yes

clean: destroy

all: clean up
