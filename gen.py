#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static site generator for slop_site.

Adapted from the generator behind beza1e1.tuxen.de.
Source files in src/ start with MIME-style metadata headers
(title:, date:, tldr:, image_src:, ...) followed by the body.
"""

import os.path
import shutil
import email  # using MIME format for src files
import configparser
from datetime import datetime
import dateutil.parser
import jinja2
import markdown

OUTDIR = "public"
SRCDIR = "src"
TMPLDIR = "template"
INLINECSS = os.path.join(TMPLDIR, "style.css")


def ensure_dir(name):
	try:
		os.makedirs(name)
	except OSError:
		pass


TMPL_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TMPLDIR))

EXTENSION_MAP = dict()


def for_extension(ext):
	def decorate(func):
		EXTENSION_MAP[ext] = func
		return func
	return decorate


# Static assets are hardlinked (or copied as fallback) into OUTDIR,
# keeping their path relative to src/.
@for_extension("css")
@for_extension("png")
@for_extension("jpg")
@for_extension("webp")
@for_extension("jpeg")
@for_extension("webm")
@for_extension("svg")
@for_extension("pdf")
@for_extension("js")
@for_extension("html")
@for_extension("py")
@for_extension("ipynb")
def hardlink_file(infile):
	assert infile.startswith(SRCDIR)
	relpath = infile[len(SRCDIR) + 1:]
	outfile = os.path.join(OUTDIR, relpath)
	os.makedirs(os.path.dirname(outfile), exist_ok=True)
	try:
		os.link(infile, outfile)
	except OSError:
		try:
			shutil.copy(infile, outfile)
		except shutil.SameFileError:
			# os.link above previously succeeded
			pass


def load_infile(infile):
	with open(infile, encoding="utf-8") as fh:
		raw = email.message_from_file(fh)
	assert not raw.is_multipart()
	vars = dict()
	for k, v in raw.items():
		vars[k] = v
	vars["infile"] = infile
	vars = refurbish_vars(vars)
	contents = raw.get_payload()
	return contents, vars


def outfile_with_ext(infile, new_ext):
	base = os.path.basename(infile)
	assert infile.startswith(SRCDIR)
	rel_dir = os.path.dirname(infile)[len(SRCDIR) + 1:]
	root, _ext = os.path.splitext(base)
	outfile = os.path.join(rel_dir, root) + new_ext
	ensure_dir(os.path.join(OUTDIR, os.path.dirname(outfile)))
	return outfile


with open(INLINECSS, encoding="utf-8") as fh:
	_INLINECSS_DATA = fh.read()


def render(vars, outfile, tmpl_name="page.html"):
	vars["base_url"] = _CONFIG["base"]["base_url"]
	vars["selfurl"] = os.path.join(vars["base_url"], outfile)
	vars["inlinecss"] = _INLINECSS_DATA
	vars["CONFIG"] = _CONFIG
	template = TMPL_ENV.get_template(tmpl_name)
	target = os.path.join(OUTDIR, outfile)
	ensure_dir(os.path.dirname(target))
	with open(target, "w", encoding="utf-8") as out:
		out.write(template.render(vars))


def cd_once(path):
	"""Remove the first directory element of path."""
	i = path.find("/")
	if i > 0:
		return path[i + 1:]
	return path


assert cd_once("bla/foo/baz.txt") == "foo/baz.txt"


def relative_prefix(infile):
	"""Return relative path to site root from infile."""
	assert infile.startswith(SRCDIR + "/")
	path = infile[len(SRCDIR) + 1:]
	depth = path.count("/")
	return "../" * depth


def refurbish_vars(vars):
	infile = vars["infile"]
	vars["title"] = vars.get("title", "No Title?!")
	vars["author"] = vars.get("author", "anon")
	vars["ROOT"] = relative_prefix(infile)
	if "date" not in vars:
		dt = datetime.fromtimestamp(os.path.getmtime(infile))
		vars["date_parsed"] = dt
		vars["date"] = dt.strftime("%Y-%m-%d")
	else:
		vars["date_parsed"] = dateutil.parser.parse(vars["date"])
	return vars


def needs_update(outfile, infile):
	"""True if the outfile must be generated anew from the infile."""
	o = os.path.join(OUTDIR, outfile)
	try:
		mt_o = os.path.getmtime(o)
	except FileNotFoundError:
		return True
	mt_i = os.path.getmtime(infile)
	return mt_i > mt_o


@for_extension("md")
@for_extension("mdwn")
@for_extension("markdown")
def markdown_handler(infile):
	contents, vars = load_infile(infile)
	outfile = outfile_with_ext(infile, ".html")
	if needs_update(outfile, infile):
		vars["contents"] = markdown.markdown(contents)
		render(vars, outfile)


@for_extension("htm")
def htm_handler(infile):
	contents, vars = load_infile(infile)
	outfile = outfile_with_ext(infile, ".html")
	if needs_update(outfile, infile):
		vars["contents"] = contents
		render(vars, outfile)


@for_extension("collection")
def collection_handler(infile):
	dirname = os.path.dirname(infile)          # prefix for generator
	relpath = dirname[len(SRCDIR):]            # prefix on website
	contents, vars = load_infile(infile)
	items = list()
	for filename in contents.split("\n"):
		f = os.path.join(dirname, filename)
		if not os.path.isfile(f):
			continue
		_, f_vars = load_infile(f)
		f_outfile = outfile_with_ext(f, ".html")
		if relpath:
			f_outfile = f_outfile[len(relpath):]
		items.append(dict(
			title=f_vars["title"],
			link=f_outfile,
			date=f_vars["date"],
			date_parsed=f_vars["date_parsed"],
			tldr=f_vars.get("tldr", ""),
			image_src=f_vars.get("image_src", ""),
		))
	items.sort(key=lambda x: x["date"], reverse=True)
	atom_outfile = outfile_with_ext(infile, ".atom")
	vars["collection"] = items
	vars["atomlink"] = cd_once(atom_outfile)
	outfile = outfile_with_ext(infile, ".html")
	vars["link"] = outfile  # feed's alternate link points to its HTML page
	render(vars, outfile, tmpl_name="collection.html")
	render(vars, atom_outfile, tmpl_name="collection.atom")


def all_infiles():
	for root, dirnames, filenames in os.walk(SRCDIR):
		for filename in filenames:
			yield os.path.join(root, filename)


_CONFIG = configparser.ConfigParser()

if __name__ == "__main__":
	ensure_dir(OUTDIR)
	_CONFIG.read("config.ini")
	for infile in all_infiles():
		if not os.path.isfile(infile):
			continue
		_ext, ext = os.path.splitext(os.path.basename(infile))
		if ext[1:] not in EXTENSION_MAP:
			print("unknown extension:", infile)
			continue
		EXTENSION_MAP[ext[1:]](infile)
