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

# Verify article links; exit 2 on dead links, add --fail-warnings in CI to also fail on unverified links
check-links *ARGS:
	test -f {{SETUP_FLAG}} || just setup
	{{ENVDIR}}/bin/python scripts/check_links.py {{ARGS}}

# Look up or create Wayback snapshots for URLs/articles (see scripts/archive.py --help)
archive *ARGS:
	python3 scripts/archive.py {{ARGS}}

shell:
	bash -c ". {{ENVDIR}}/bin/activate && bash"
