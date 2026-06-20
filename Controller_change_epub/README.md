# OpenSpec to mark2epub helper

This folder contains a Python helper that turns an OpenSpec change folder into a mark2epub-ready source directory.

## Example

From the repository root, run:

python Controller_change_epub/openspec_to_epub_source.py openspec/changes/add-multi-controller-support --author "Chris"

The script generates:
- chapter markdown files
- css/style.css
- images/
- description.json

Then build the EPUB with the existing converter:

python mark2epub.py Controller_change_epub/add-multi-controller-support multi_controller_proposal.epub
