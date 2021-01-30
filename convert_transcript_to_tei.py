#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 18:03:31 2021

@author: florian
"""

import re

def read_txt_from_file(file):
    """
    """
    with open(file, "r", encoding="utf8") as current_file:
        txt = current_file.read()
        return txt

def write_txt_to_file(file, txt):
    """
    """
    with open(file, "w", encoding="utf8") as current_file:
        current_file.write(f"{txt}")

def read_metadata(txt):
    """
    """
    metadata = {}
    
    metadata_list = [
        ("author", "a"),
        ("title", "t"),
        ("siglum", "s"),
        ("transcriber", "tr"),
        ("transcriber_initials", "tri")]
    
    for item in metadata_list:
        metadata[item[0]] = re.search('<'+item[1]+'>(.*?)</'+item[1]+'>', txt).group(1)
        txt = re.sub(f'<{item[1]}>(.*?)</{item[1]}>\n','',txt)
    
    return metadata, txt

def create_teiHeader(title, author, transcriber, transcriber_initials, siglum):
    teiHeader = ('<teiHeader>' +'\n'+
                 '<fileDesc>' +'\n'+
                 '<titleStmt>' +'\n'+
                 '<title>' + title + '</title>' +'\n'+
                 '<author>' + author + '</author>' +'\n'+
                 '<respStmt>' +'\n'+
                 '<name xml:id="' + transcriber_initials + '">' + transcriber + '</name>' +'\n'+
                 '<resp>manuscript transcription</resp>' +'\n'+
                 '</respStmt>' +'\n'+
                 '</titleStmt>' +'\n'+
                 '<publicationStmt><p>unpublished</p></publicationStmt>' +'\n'+
                 '<sourceDesc>' +'\n'+
                 '<listWit>' +'\n'+
                 '<witness xml:id="' + siglum + '"></witness>' +'\n'+
                 '</listWit>' +'\n'+
                 '</sourceDesc>' +'\n'+
                 '</fileDesc>' +'\n'+
                 '</teiHeader>')
    return teiHeader

def convert_linebreaks(txt):
    """
    """
    txt = re.sub('\n','<lb/> ', txt)
    return txt

def convert_pagebreaks(txt, siglum):
    """
    """
    txt = re.sub('\|fol\. ([0-9]{1,3}[rv])\|','<pb edRef="#'+siglum+'" n="'+r'\1'+'"/> ', txt)
    return txt

def add_paragraphs(txt):
    """
    """
    txt = '<p>' + txt + '</p>'
    txt = re.sub('//', '</p><p>', txt)
    return txt

def convert_punctuation(txt):
    """
    """
    punctuation_list = {
        "U002E": ".",
        "U003A": ":",
        "U0700" : "܀",
        "U0707" : "܇",
        "U0709" : "܆"}
    
    for k,v in punctuation_list.items():
        txt = txt.replace(v,'<pc>'+v+'</pc>')
    return txt

def convert_rubrics(txt):
    """
    """
    txt = re.sub('<r>(.*?)</r>','<rubric>'+r'\1'+'</rubric>', txt)
    return txt

def convert_glosses(txt, siglum):
    """
    """
    gloss_annotation = re.search('<m(.)>(.*?)</m>', txt)
    place = gloss_annotation.group(1)
    gloss = gloss_annotation.group(2)
    if place == "r":
        place = "right"
    elif place == "l":
        place = "left"
    elif place == "t":
        place = "top"
    elif place == "b":
        place = "bottom"
    elif place == "a":
        place = "above"
    
    txt = re.sub('<m.>.*?</m>','<add edRef="#'+siglum+'" place="'+place+'">'+gloss+'</add>', txt)
    return txt

def add_tei_structure(txt, teiHeader):
    """
    """
    teiPreamble = ('<?xml version="1.0" encoding="UTF-8"?>' +'\n')
               #'<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>' +'\n'+
               #'<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>' +'\n')
               
    teiFrameOpen = '<TEI xmlns="http://www.tei-c.org/ns/1.0">' +'\n'
    teiFrameClose  = '</TEI>'
    txt = teiPreamble + teiFrameOpen + teiHeader + "<text><body>" + txt + "</body></text>" + teiFrameClose
    return txt

def process(file):
    txt = read_txt_from_file(file)
    (metadata, txt) = read_metadata(txt)
    header = create_teiHeader(
        metadata["title"],
        metadata["author"],
        metadata["transcriber"],
        metadata["transcriber_initials"],
        metadata["siglum"]
        )
    txt = convert_linebreaks(txt)
    txt = convert_pagebreaks(txt, metadata["siglum"])
    txt = add_paragraphs(txt)
    txt = convert_punctuation(txt)
    txt = convert_rubrics(txt)
    txt = convert_glosses(txt, metadata["siglum"])
    txt = add_tei_structure(txt, header)
    write_txt_to_file('./output.xml',txt)