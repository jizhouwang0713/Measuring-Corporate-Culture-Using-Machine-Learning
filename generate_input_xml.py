# %%
import json
import os
import pandas as pd
from bs4 import BeautifulSoup

# %%
# with open('C:/Users/jizhouw0/Desktop/sample_transcripts_xml/20000426-16448-C.xml') as f:
#     file = f.read()


# call = BeautifulSoup(file, 'xml')

# %%
# experiment with the meta section
# date = call.find('datedf').text if call.find('datedf') != None else "NA"
# transcript_id = call.find('transcript').get('id2')
# print(transcript_id)

# company = call.find_all('company')
# for c in company: print(type(company), type(c.text))


# %%
# experiment with the management discussion section
# discussion = call.find('section', {'name': 'MANAGEMENT DISCUSSION SECTION'}).find_all('speaker')
# Note that the first sectence is an introduction and is not part of the earnings call
# Implementation: we wnat to collect all those sentences somewhere -- not important
# print(discussion[0].get('id') is None)

# full_discussion_list = []
# for part in discussion:
#     if part.get('id') not in (None, '0'):
#         paragraphs = part.find_all('p')
#         full_discussion_list.extend([paragraph.text for paragraph in paragraphs])
        
# full_discussion = " ".join(full_discussion_list)
# print(full_discussion)
        
    

# %%
# experiment with the Q&A section
# QA = call.find('section', {'name': 'Q&A'}).find_all('speaker')
# full_QA_list = []
# for part in QA:
#     if part.get('id') != "0":
#         paragraphs = part.find_all('p')
#         full_QA_list.extend([paragraph.text for paragraph in paragraphs])
        
# full_QA = " ".join(full_QA_list)
# print(full_QA)

# %%
# define directory where the transcripts are stored 
directory = "C:/Users/jizhouw0/Desktop/sample_transcripts_xml"

# define a helper function -- line_counter
def line_counter(a_file):
    """Count the number of lines in a text file
    
    Arguments:
        a_file {str or Path} -- input text file
    
    Returns:
        int -- number of lines in the file
    """
    n_lines = 0
    with open(a_file, "rb") as f:
        n_lines = sum(1 for _ in f)
    return n_lines

# %%
# We define a function that is used to extract desired parts from an earnings call transcript
def extract_sections(path_str):
    # initialize two variables to indicate whether the scripted and unscripted sections exist
    no_management_discussion = 0
    no_QA = 0
    
    with open(path_str) as f: 
            file = f.read()
            
    call = BeautifulSoup(file, 'xml')
    
    # First deal with the meta data 
    transcript_id = call.find('transcript').get('id') if call.find('transcript').get('id') != None else 'NA'
    date = call.find('date').text if call.find('date') != None else 'NA'
    title = call.find('title').text if call.find('title') != None else 'NA'
    company_id = call.find('company').text if call.find('company') != None else 'NA'
    
    id2firms["document_id"].append(transcript_id)
    id2firms["firm_id"].append(company_id)
    id2firms["time"].append(date)  
    id2firms["transcript_title"].append(title)
    
    # Then deal with the management discussion section
    if call.find('section', {'name': 'MANAGEMENT DISCUSSION SECTION'}) == None:
        no_management_discussion = 1
        full_discussion = ""
    else:
        discussion = call.find('section', {'name': 'MANAGEMENT DISCUSSION SECTION'}).find_all('speaker')
        # Note that we exclude the words said by the moderator (id == 0)
        
        full_discussion_list = []
        for part in discussion:
            if part.get('id') not in (None, '0'):
                paragraphs = part.find_all('p')
                full_discussion_list.extend([paragraph.text for paragraph in paragraphs])
                
        full_discussion_raw = " ".join(full_discussion_list).replace('\r', '').replace('\n', '')
        # remove any extra space
        full_discussion = " ".join(full_discussion_raw.split())
        
    # Finally deal with the Q & A section
    if  call.find('section', {'name': 'Q&A'}) == None:
        no_QA = 1
        full_QA = ""
    else:
        QA = call.find('section', {'name': 'Q&A'}).find_all('speaker')
        full_QA_list = []
        for part in QA:
            if part.get('id') != "0":
                paragraphs = part.find_all('p')
                full_QA_list.extend([paragraph.text for paragraph in paragraphs])
                
        full_QA_raw = " ".join(full_QA_list).replace('\r', '').replace('\n', '')
        # remove any extra space
        full_QA = " ".join(full_QA_raw.split())
        
    # Combine management discussion with Q&A to form the complete transcripts
    full_transcript = full_discussion + " " + full_QA
    
    # Output management discussion and Q&A to text files 
    with open('C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_both.txt', 'a', encoding="utf-8") as out_f: 
        out_f.write(full_transcript + '\n')
        
    
    with open('C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_unscripted.txt', 'a', encoding="utf-8") as out_f: 
        out_f.write(full_QA + '\n')
        
        
    with open('C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_scripted.txt', 'a', encoding="utf-8") as out_f: 
        out_f.write(full_discussion + '\n')
    
    # Return whether the scripted and unscripted sections exist
    return no_management_discussion, no_QA
    
    

# %%
# We iteratre over all the transripts (in xml format) and generate three text files as inout for the ML algorithm 
# scripted section, Q & A section, and both
existence_dict = {}
path_dict = {}
id2firms = {"document_id":[], "firm_id": [], "time": [], "transcript_title": []}
doc_count_C, doc_count_T, doc_count_total, doc_count_not_included = 0, 0, 0, 0
problematic_file_id = 0

# When we loop over the files for the first time, we only focus on those "corrected" transcripts
for filename in os.scandir(directory):
    if filename.is_file():
        doc_count_total += 1
        if filename.path.find('-C') != -1: 
            doc_count_C += 1
            new_path = filename.path.replace('-C', "")
            path_dict[new_path] = doc_count_C
            
            no_management_discussion, no_QA = extract_sections(filename.path)
            if no_management_discussion + no_QA > 0:
                problematic_file_id += 1
                data_row = [0, 0, filename.path.replace('\\', '/')]
                if no_management_discussion == 1:
                    data_row[0] = 1
                if no_QA == 1:
                    data_row[1] = 1
                
                existence_dict[problematic_file_id] = data_row
                
# Now we loop over the files for the second time. We focus on the raw transcripts.
for filename in os.scandir(directory):
    if filename.is_file(): 
        if filename.path.find('-T') != -1: 
            if filename.path.replace('-T', "") not in path_dict:
                doc_count_T += 1
                
                no_management_discussion, no_QA = extract_sections(filename.path)
                if no_management_discussion + no_QA > 0:
                    problematic_file_id += 1
                    data_row = [0, 0, filename.path.replace('\\', '/')]
                    if no_management_discussion == 1:
                        data_row[0] = 1
                    if no_QA == 1:
                        data_row[1] = 1
                    
                    existence_dict[problematic_file_id] = data_row
                    
            else:
                doc_count_not_included += 1
                continue
            
            
# Output the text file "document_id"     
document_id = map(str, id2firms["document_id"]) 
with open('C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/document_ids.txt', 'w') as f: 
    f.write('\n'.join(document_id))
    
# Output the csv file "id2firms"
df_id2firms = pd.DataFrame(data=id2firms)
df_id2firms[["document_id", "firm_id"]] = df_id2firms[["document_id", "firm_id"]].astype(str)
df_id2firms.to_csv('C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/id2firms.csv', header = True, index = False)

# Output the text file "meta_data"
with open('C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/meta_data.txt', 'a', encoding="utf-8") as f: 
    f.write(f'There are a total of {doc_count_total} transcripts in the directory' + '\n')
    f.write(f'The final text file includes {doc_count_C} corrected transcipts' + '\n')
    f.write(f'The final text file includes {doc_count_T} raw transcripts' + '\n')
    f.write(f'{doc_count_not_included} raw transcripts also have the corrected versions, so the raw versions are not included')
    
# Output a summary of files lacking either the scripted or the unscripted section
df_missing_sections = pd.DataFrame.from_dict(existence_dict, orient='index', columns=['no_management_discussion', 'no_Q&A', 'file_path'])
df_missing_sections.to_csv('C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/missing_sections.csv', header = True, index = False)

# Assert that line numbers equal
assert line_counter("C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_unscripted.txt") == doc_count_C + doc_count_T, "Line Number Differs From Document Count!"
assert df_id2firms.shape[0] == line_counter("C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_both.txt"), "Number of IDs Differs From Number of Documents!"
      


