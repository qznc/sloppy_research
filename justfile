# Static site generator for Sloppy Research
# Requires https://github.com/casey/just

default: gen

ENVDIR := ".env_" + `hostname`
SETUP_FLAG := ENVDIR + "/setup_done"

setup:
	mkdir -p {{ENVDIR}}
	python3 -m venv {{ENVDIR}}
	{{ENVDIR}}/bin/pip install -r requirements.txt
	touch {{SETUP_FLAG}}

gen:
	test -f {{SETUP_FLAG}} || just setup
	{{ENVDIR}}/bin/python gen.py

clean:
	rm -rf public

shell:
	bash -c ". {{ENVDIR}}/bin/activate && bash"
