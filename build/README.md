# Rebuilding the catalog

Source: the two Document Logs on SharePoint (Projects/FAT - First American Title/FAT-IA-Big River-NRG-2056/- Management/Trackers/):
"Big River Document Log - JONDESK rows.csv" and "Big River Document Log - LT04 rows.csv". fileit.py and the scan-filing runner
append a row there for every PDF they file to the parcel Documents folders (and copy into Imager Documents).

1. Read every page of both CSVs (M365 connector read_resource, startPage 1, 2, 3...) and save each page as a file in one folder.
2. `python3 build/refresh.py <that folder>` -> prints CHANGED (index.html rewritten) or UNCHANGED.
3. If CHANGED: commit index.html and build/docs.sha, push to main. GitHub Pages republishes in a minute or two.

pmap.json maps parcel -> file number; folders.txt holds the file folder names. Add new parcels/files there if Big River grows.
