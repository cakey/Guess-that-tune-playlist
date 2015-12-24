# -*- coding: utf-8 -*-

import collections
import json
import re

import SPARQLWrapper

def most_common():
    counter = collections.Counter()

    ignorelist = ["The Cavendish Orchestra","Terry Cavendish"]

    with open("processed_24_dec_2015_backup.txt") as o:
        for line in o:
            parts = line.split(" – ")
            artist = parts[0]
            # crude measure of feat, for more accurate counts
            if "Earth, Wind & Fire" in artist:
                counter["Earth, Wind & Fire"] += 1
            else:
                for a in artist.split(","):
                    a = a.strip()
                    if not a in ignorelist:
                        counter[a] += 1


    for x in counter.most_common(40):
        print x[1], "\t", x[0]

def years():
    sparql = SPARQLWrapper.SPARQLWrapper("http://dbpedia.org/sparql")

    year_counter = counter = collections.Counter()
    unfound = []
    total = 0
    with open("processed_24_dec_2015_backup.txt") as o:
        for line in o:
            total += 1
            words = []
            line = line.strip()
            fixed_line = re.sub('Original Mix|Explicit|Radio Version|Dirty Radio Edit|Radio Edit|Original Radio Edit|\(Download\)|, Richard Bedford|Remastered Version|Remastered Version|Remastered Album Version|Original Version| - Original Mix|Single Version| - Live|Single Edit|LP Version|BBC Radio 1 Live Lounge|Original London Cast|Michael Reed|Theme from|The| - Edit|\(feat .*\)|\(Feat .*\)|\(featuring .*\)|Theme From| - Original$|/ Mono|Digital Remaster|Original mix|/Soundtrack Version|Extended Version|New Sound Remastered|Explicit Version|\(Mono\)|Album Version|45 Version|Radio Mix|\(.*\)|New Stereo Mix|Stereo Remastered Version|Original Album Version|Original Mono Version|Remixed Version|Soundtrack Version|Radio edit|\[.*\]|/ Stereo$|Club Mix|Album Verision|Alternate Version|Dance Mix|Revised Album Version', '', line)
            blacklist = ["REMASTER", "REMASTERED", "Y"]
            for p in fixed_line.translate(None, ',()').split(" – "):
                for w in p.split(" "):
                    if w.isalnum() and not w.isdigit() and not w.upper() in blacklist and len(w) > 2:
                        words.append("\""+w.upper()+"\"")
            search_string = " AND ".join(words)
            query = """
                PREFIX dbo: <http://dbpedia.org/ontology/>

                select ?s1, ?date where
                {
                    ?s1 dbo:abstract ?o1 .
                    ?o1 bif:contains ' (%s) ' option ( score ?sc ) .
                    ?s1 dbo:releaseDate ?date .

                }
                order by desc ( ?sc * 3e-1 + sql:rnk_scale ( <LONG::IRI_RANK> ( ?s1 ) ) ) limit 1 offset 0
            """ % (search_string)
            sparql.setQuery(query)
            sparql.setReturnFormat(SPARQLWrapper.JSON)
            results = sparql.query().convert()

            # print query
            b = results["results"]["bindings"]
            if len(b) > 0:
                print "FOUND__"
                print line
                print b[0]["date"]["value"]
                year = b[0]["date"]["value"].split("-")[0]
                year_counter[year] += 1
                print b[0]["s1"]["value"]
            else:
                print "\tUNFOUND__"
                print "\t", line
                print "\t", search_string
                unfound.append(line)
            # print
            if total >= 5000:
                break

    for x in year_counter.most_common():
        print x[1], "\t", x[0]

    print "\n".join(unfound)
years()
