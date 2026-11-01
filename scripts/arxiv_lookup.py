import sys, re, time, urllib.parse, urllib.request
def look(title):
    q = urllib.parse.urlencode({"search_query": 'ti:"%s"' % title, "max_results": 2})
    x = urllib.request.urlopen("https://export.arxiv.org/api/query?" + q, timeout=40).read().decode()
    out = []
    for e in re.findall(r"<entry>(.*?)</entry>", x, re.S):
        out.append((re.search(r"<id>http://arxiv.org/abs/([^<]*?)</id>", e).group(1),
                    re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", e, re.S).group(1)).strip(),
                    "; ".join(re.findall(r"<name>(.*?)</name>", e)[:3]), re.search(r"<published>(\d{4})", e).group(1)))
    return out
for t in sys.argv[1:]:
    r = look(t); print(">>", t); [print("  ", *x, sep=" | ") for x in r[:1]]; time.sleep(3)
