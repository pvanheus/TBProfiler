import time
from .reformat import *

_DRUGS = [
    'rifampicin', 'isoniazid', 'ethambutol', 'pyrazinamide', 'streptomycin',
    'fluoroquinolones', 'amikacin', 'capreomycin', 'kanamycin',
    'cycloserine',  'ethionamide', 'clofazimine', 'para-aminosalicylic_acid',
    'delamanid', 'bedaquiline', 'linezolid'
]

def lineagejson2text(x):
	textlines = []
	for l in x:
		textlines.append("%(lin)s\t%(family)s\t%(spoligotype)s\t%(rd)s\t%(frac)s" % l)
	return "\n".join(textlines)

def dict_list2text(l,columns = None, mappings = None):
	headings = list(l[0].keys()) if not columns else columns
	rows = []
	header = "\t".join([mappings[x].title() if (mappings!=None and x in mappings) else x.title() for x in headings])
	for row in l:
		r = "\t".join(["%.3f" % row[x] if isinstance(row[x],float) else str(row[x]).replace("_", " ") for x in headings])
		rows.append(r)
	str_rows = "\n".join(rows)
	return  "%s\n%s\n" % (header,str_rows)

def dict_list2csv(l,columns = None, mappings = None):
	headings = list(l[0].keys()) if not columns else columns
	rows = []
	header = ",".join([mappings[x].title() if (mappings!=None and x in mappings) else x.title() for x in headings])
	for row in l:
		r = ",".join(["%.3f" % row[x] if isinstance(row[x],float) else "\"%s\"" % str(row[x]).replace("_", " ") for x in headings])
		rows.append(r)
	str_rows = "\n".join(rows)
	return  "%s\n%s\n" % (header,str_rows)



def load_text(text_strings):
	return r"""
TBProfiler report
=================

The following report has been generated by TBProfiler.

Summary
-------
ID: %(id)s
Date: %(date)s
Strain: %(strain)s
Drug-resistance: %(drtype)s

Lineage report
--------------
%(lineage_report)s

Resistance report
-----------------
%(dr_report)s

Resistance variants report
-----------------
%(dr_var_report)s

Other variants report
---------------------
%(other_var_report)s

Analysis pipeline specifications
--------------------------------
Pipeline version: %(version)s
Database version: %(db_version)s
%(pipeline)s

Disclaimer
----------
This tool is for Research Use Only and is offered free foruse. The London School
of Hygiene and Tropical Medicine shall have no liability for any loss or damages
of any kind, however sustained relating to the use of this tool.

Citation
--------
Coll, F. et al. Rapid determination of anti-tuberculosis drug resistance from
whole-genome sequences. Genome Medicine 7, 51. 2015
""" % text_strings

def load_csv(text_strings):
	return r"""
TBProfiler report
--------------

Summary
-------
ID,%(id)s
Date,%(date)s
Strain,%(strain)s
Drug-resistance,%(drtype)s

Lineage report
--------------
%(lineage_report)s

Resistance report
-----------------
%(dr_report)s

Other variants report
---------------------
%(other_var_report)s

Analysis pipeline specifications
--------------------------------
Pipeline version,%(version)s
Database version,"%(db_version)s"
%(pipeline)s""" % text_strings


def write_text(json_results,conf,outfile,columns = None,reporting_af = 0.0):
	json_results = get_summary(json_results,conf,columns = columns,reporting_af=reporting_af)
	json_results["drug_table"] = [[y for y in json_results["drug_table"] if y["Drug"].upper()==d.upper()][0] for d in _DRUGS]
	uniq_dr_variants = {}
	for var in json_results["dr_variants"]:
		if var["change"] in uniq_dr_variants:
			uniq_dr_variants[var["change"]]["drug"] += ","+var["drug"]
		else:
			uniq_dr_variants[var["change"]] = var
	text_strings = {}
	text_strings["id"] = json_results["id"]
	text_strings["date"] = time.ctime()
	text_strings["strain"] = json_results["sublin"]
	text_strings["drtype"] = json_results["drtype"]
	text_strings["dr_report"] = dict_list2text(json_results["drug_table"],["Drug","Genotypic Resistance","Mutations"]+columns if columns else [])
	text_strings["lineage_report"] = dict_list2text(json_results["lineage"],["lin","frac","family","spoligotype","rd"],{"lin":"Lineage","frac":"Estimated fraction"})
	text_strings["dr_var_report"] = dict_list2text(list(uniq_dr_variants.values()),["genome_pos","locus_tag","gene","change","freq","drug"],{"genome_pos":"Genome Position","locus_tag":"Locus Tag","freq":"Estimated fraction"})
	text_strings["other_var_report"] = dict_list2text(json_results["other_variants"],["genome_pos","locus_tag","gene","change","freq"],{"genome_pos":"Genome Position","locus_tag":"Locus Tag","freq":"Estimated fraction"})
	text_strings["pipeline"] = dict_list2text(json_results["pipline_table"],["Analysis","Program"])
	text_strings["version"] = json_results["tbprofiler_version"]
	text_strings["db_version"] = "%s_%s_%s_%s" % (json_results["db_version"]["name"],json_results["db_version"]["commit"],json_results["db_version"]["Author"],json_results["db_version"]["Date"])
	o = open(outfile,"w")
	o.write(load_text(text_strings))
	o.close()







def write_csv(json_results,conf,outfile,columns = None):
	json_results = get_summary(json_results,conf,columns = columns)
	json_results["drug_table"] = [[y for y in json_results["drug_table"] if y["Drug"].upper()==d.upper()][0] for d in _DRUGS]
	csv_strings = {}
	csv_strings["id"] = json_results["id"]
	csv_strings["date"] = time.ctime()
	csv_strings["strain"] = json_results["sublin"]
	csv_strings["drtype"] = json_results["drtype"]
	csv_strings["dr_report"] = dict_list2csv(json_results["drug_table"],["Drug","Genotypic Resistance","Mutations"]+columns if columns else [])
	csv_strings["lineage_report"] = dict_list2csv(json_results["lineage"],["lin","frac","family","spoligotype","rd"],{"lin":"Lineage","frac":"Estimated fraction"})
	csv_strings["other_var_report"] = dict_list2csv(json_results["other_variants"],["genome_pos","locus_tag","change","freq"],{"genome_pos":"Genome Position","locus_tag":"Locus Tag","freq":"Estimated fraction"})
	csv_strings["pipeline"] = dict_list2csv(json_results["pipline_table"],["Analysis","Program"])
	csv_strings["version"] = json_results["tbprofiler_version"]
	csv_strings["db_version"] = "%s_%s_%s_%s" % (json_results["db_version"]["name"],json_results["db_version"]["commit"],json_results["db_version"]["Author"],json_results["db_version"]["Date"])
	o = open(outfile,"w")
	o.write(load_csv(csv_strings))
	o.close()
