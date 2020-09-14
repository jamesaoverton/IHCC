#!/usr/bin/env python
# coding: utf-8

"""
This script uses a mix of IHCC services to generate mapping suggestions for data dictionaries.
The input is a ROBOT template with the usual IHCC data dictionary. This dictionary is augmented with
Suggested mappings, which are added the 'Suggested Mappings' column of the template.
author: Nico Matentzoglu for Knocean Inc., 26 August 2020
"""

import pandas as pd
from argparse import ArgumentParser
from lib import load_ihcc_config, map_term


parser = ArgumentParser()
parser.add_argument("-c", "--config", dest="config_file",
                    help="Config file", metavar="FILE")
parser.add_argument("-t", "--template", dest="tsv_path",
                    help="Template file file", metavar="FILE")
parser.add_argument("-o", "--output", dest="tsv_out_path",
                    help="Output file", metavar="FILE")
args = parser.parse_args()

## Loading config
config = load_ihcc_config(args.config_file)
zooma_annotate=config["zooma_annotate"]
oxo_mapping=config["oxo_mapping"]
ols_term=config["ols_term"]
ols_oboid=config["ols_oboid"]

confidence_map = ["HIGH", "GOOD", "MEDIUM", "LOW"] # These are the default confidence levels from Zooma
print(config)

## Loading data
tsv=pd.read_csv(args.tsv_path,sep="\t")
del tsv['Suggested Categories']
tsv_terms=tsv['Label'].values[2:]

## Generating matches
matches=[]

for term in tsv_terms:
    #print("Matching "+term)
    matches.extend(map_term(term,zooma_annotate, ols_term, ols_oboid))
                        
df=pd.DataFrame(matches,columns=['term','match','match_label','confidence'])
df

## Transform matches into the right format and merge into template
dfs=df[~df['match'].str.startswith("https://purl.ihccglobal.org/")].copy()
dfs['Suggested Categories']=dfs[['confidence', 'match', 'match_label']].agg(' '.join, axis=1)
dfs=dfs[['term','Suggested Categories']]
dfsagg=dfs.groupby('term', as_index=False).agg(lambda x: ' | '.join(set(x.dropna())))
dfx = pd.merge(tsv, dfsagg, how='left', left_on=['Label'], right_on=['term'])
del dfx['term']

## Save template
with open(args.tsv_out_path,'w') as write_csv:
    write_csv.write(dfx.to_csv(sep='\t', index=False))

