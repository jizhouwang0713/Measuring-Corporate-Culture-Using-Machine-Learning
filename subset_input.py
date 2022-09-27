# %%
import pandas as pd

# %%
document_id_set = set(map(str, pd.read_csv('C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcript_list.csv')["document_id"]))

with open("C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/document_ids.txt", "r") as f_id:
    lines = f_id.readlines()

index_list = set()
for i, line in enumerate(lines):
    if line.strip("\n") in document_id_set:
        index_list.add(i)
print(f"The number of documents in the subsample is {len(index_list)}")
        



# %%
input_list = ["C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_both.txt",
             "C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_scripted.txt",
             "C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_unscripted.txt"]

output_list = ["C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_both_sub.txt",
             "C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_scripted_sub.txt",
             "C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_unscripted_sub.txt"]

for j, input in enumerate(input_list):
    with open(input, "r") as f_both:
        lines = f_both.readlines()
    with open(output_list[j], "w") as f_both_sub:
        for i, line in enumerate(lines):
            if i in index_list:
                f_both_sub.write(line)

# %%
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

# Assert the line numbers are correct
assert len(index_list) == line_counter("C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_both_sub.txt"), "Number of transcripts incorrect (both)!"
assert len(index_list) == line_counter("C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_scripted_sub.txt"), "Number of transcripts incorrect (scripted)!"
assert len(index_list) == line_counter("C:/Users/jizhouw0/Desktop/sample_transcripts_xml/text_all/transcripts_unscripted_sub.txt"), "Number of transcripts incorrect (unscripted)!"
   


