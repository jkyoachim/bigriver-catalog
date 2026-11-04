# Rebuilding the pull list page (pull-list/index.html)

1. Build the day's seed JSON (rows, done, recheck, meta) from the day's pull-list rows CSV and the book-page lookups CSV.
   The seed builder lives in the project files ("Big River pull assignments/Pull list page/site/").
2. `python3 build/pull-list/gen.py build/pull-list/template.html <seed.json> pull-list/index.html`
3. Commit pull-list/index.html and push to main. Fetch and rebase first: the hourly catalog refresh also pushes to main.

Row keys ('r' + sha1(date|cite|grantor|grantee)[:9]) must stay stable so ticks saved on the crew's phones keep matching.
