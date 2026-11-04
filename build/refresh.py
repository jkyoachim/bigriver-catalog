"""Rebuild the Big River catalog page from the Document Log CSV pages.
usage: python3 build/refresh.py RAW_DIR
RAW_DIR holds every page of "Big River Document Log - JONDESK rows.csv" and "- LT04 rows.csv" as read through the
M365 connector (any file names; the connector's "[page N ...]" footers are stripped). Writes index.html at repo root
only if the document list changed, and prints CHANGED or UNCHANGED."""
import csv, io, re, json, sys, gzip, base64, os, glob, collections, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
def load(p):
    t = open(p, encoding='utf-8-sig').read()
    t = re.sub(r'\n*\[(page|truncated)[^\]]*\]\s*$', '', t.rstrip()) + "\n"
    return list(csv.DictReader(io.StringIO(t)))
rows = []
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*'))):
    r = load(f); print(os.path.basename(f), len(r)); rows += r
by = collections.OrderedDict()
for r in rows:
    k = (r.get('file_name') or '').strip()
    if not k: continue
    if k in by:
        ps = set(filter(None, by[k]['parcels'].split(';'))) | set(filter(None, (r.get('parcels') or '').split(';')))
        by[k]['parcels'] = ';'.join(sorted(ps))
    else: by[k] = {c: (r.get(c) or '') for c in ['logged','file_name','parcels','doc_type','recorded','book_page_or_inst','grantor','grantee','legal_summary','source']}
pmap = json.load(open(os.path.join(HERE, 'pmap.json')))
folders = dict(l.split(' ', 1) for l in open(os.path.join(HERE, 'folders.txt')).read().strip().split('\n'))
def cat(t):
    u = (t or '').upper()
    if 'PATENT' in u: return 'Patent'
    if re.search(r'SATISF|RELEASE|^REL\b|PARTIAL', u): return 'Release / satisfaction'
    if re.search(r'ASSIGNMENT OF MORT|SUBORDINAT', u): return 'Mortgage assignment / subordination'
    if re.search(r'MORTGAGE|DEED OF TRUST|^MTG|^MORT', u): return 'Mortgage'
    if re.search(r'UCC|LIEN|JUDG|IRS|TAX LIEN', u): return 'Lien / UCC / judgment'
    if re.search(r'EASE|RIGHT OF WAY|ROW\b', u): return 'Easement'
    if re.search(r'LEASE|OIL|GAS|MINERAL', u): return 'Lease / minerals'
    if re.search(r'SURVEY|PLAT', u): return 'Survey / plat'
    if re.search(r'CONTRACT', u): return 'Contract'
    if re.search(r'COURT|PROBATE|ESTATE|DECREE|AFF|COD|CHANGE OF TITLE|WILL', u): return 'Court / probate / affidavit'
    if re.search(r'WARRANT|^WD|^WAR|^WTY|QUIT|^QC|DEED|^SHF|^TRD|^GD\b|^TAX\b|SHERIFF|^REF|REFEREE|^EXR|EXECUT|^ADM|^GDN|GUARD|TAX DEED|TREASURER|CONVEY', u): return 'Deed'
    return 'Other'
def src(s):
    if 'arcasearch' in s.lower(): return 'ArcaSearch index page'
    if s.startswith('ILR'): return 'Iowa Land Records'
    if 'Family' in s: return 'FamilySearch'
    if 'BLM' in s: return 'BLM GLO'
    if 'vault' in s.lower(): return 'Courthouse vault scan'
    return s
out = []; unm = set()
for x in by.values():
    ps = [p for p in x['parcels'].split(';') if p]
    fs = sorted({pmap[p] for p in ps if p in pmap}); unm |= {p for p in ps if p not in pmap}
    idx = 'arcasearch' in x['source'].lower() or x['file_name'].startswith('INDEX - ')
    out.append([x['recorded'], x['doc_type'], 'Index page' if idx else cat(x['doc_type']), x['book_page_or_inst'], x['grantor'], x['grantee'],
                x['legal_summary'].replace('System.Object[]', ''), src(x['source']), ';'.join(fs), ';'.join(ps), x['file_name'], x['logged']])
out.sort(key=lambda r: (r[0], r[10]))
print('instruments', len(out), 'parcels not mapped to a file:', sorted(unm))
if len(out) < 1000: sys.exit('ABORT: fewer than 1,000 instruments read; a log page is probably missing')
state = os.path.join(HERE, 'docs.sha')
import hashlib; h = hashlib.sha256(json.dumps(out).encode()).hexdigest()
if os.path.exists(state) and open(state).read().strip() == h: print('UNCHANGED'); sys.exit(0)
data = {'built': datetime.date.today().isoformat(), 'docs': out, 'files': folders, 'pmap': pmap}
raw = gzip.compress(json.dumps(data, separators=(',', ':')).encode(), 9)
page = open(os.path.join(HERE, 'template.html')).read().replace('__PAYLOAD__', json.dumps({'plain': True, 'data': base64.b64encode(raw).decode()}))
open(os.path.join(ROOT, 'index.html'), 'w').write(page); open(state, 'w').write(h)
print('CHANGED')
