
from nltk import ParentedTree
from ast import Assert
import string
import os

#Print text in a file
def print_file(filename):
    with open(filename, "r") as f:
        print(f.read())

def deal_with_end_dot(words):
    '''Replace '.' at the end of the word with space'''
    remove_index = []
    for i in range(len(words)):
        if words[i].word == '.':#End of sentence
            assert i -1 >= 0
            #If string end with '.', replace it with ' .'
            if words[i-1].word.endswith('.')  and words[i-1].word !='...': #Special case e.g. U.S.
                remove_index.append(i)

    
    return [ words[i] for i in range(len(words)) if i not in remove_index]


def replace_bracket(text):
    '''Replace bracket in the text with space'''
    #Replace '-LRB-' with '('
    text = text.replace('-LRB-', '(')
    #Replace '-RRB-' with ')'
    text = text.replace('-RRB-', ')')
    #Replace '-LSB-' with '['
    text = text.replace('-LSB-', '[')
    #Replace '-RSB-' with ']'
    text = text.replace('-RSB-', ']')
    #Replace '-LCB-' with '{'
    text = text.replace('-LCB-', '{')
    #Replace '-RCB-' with '}'
    text = text.replace('-RCB-', '}')
    return text

#read text file
def read_text_file(filename):
    trees = []
    tree = ''
    with open(filename, "r") as f:
        for line in f:
            #If line start with '((S', it is a sentence
            if line.startswith(' '):
                tree += line
                tree += '\n'
            else:
                if tree != '':
                    trees.append(tree)
                tree = line
        trees.append(tree)   
    return trees



# Read tree from text file
def read_tree(filename):
    trees = []
    text = read_text_file(filename)

    for tree in text:
        trees.append(ParentedTree.fromstring(tree))
    return trees


def get_char_index_table(filename,debug = False):
    trees = read_tree(filename)
    # for tree in trees:
    #     tree.pretty_print()

    char_index_table = {
    'char':[]
    ,'index':[]
    ,'TreeId' : []
    ,'leafId' : []
        }
    treeId = 0
    for tree in trees:
        words_list = []
        byte_list = []
        for leaf in tree.leaves():
            words_list.append(leaf.split('{')[0])
            byte_list.append(leaf.split('{')[1].split('}')[0])

        #print(words_list, byte_list)

        for i in range(len(words_list)):

            ### Preprocessing
            #Replace '\\', '\/' with '\' and '/'
            words_list[i] = words_list[i].replace('\\\\', '\\')
            words_list[i] = words_list[i].replace('\/', '/')
            words_list[i] = words_list[i].replace('\*', '*')

            words_list[i] = replace_bracket(words_list[i])
            
            
            #Get the start and end byte span of the word
            byte_span = byte_list[i].split('.') # '4..9' to ['4','','9']
            base_index = int(byte_span[0])
            end_byte_span = int(byte_span[-1])

            ### Special cases: 
            if base_index == end_byte_span: #None '*-1' or '*'  or '0'
                #log error
                if debug:
                    print("skip: ", words_list[i], ", byte-span:", byte_list[i])
                continue

            ### Special case: '' ``
            if  words_list[i] == '``' or words_list[i] == "''":
                #print("special case: " ,words_list[i])
                char_index_table['char'].append(words_list[i][0])
                char_index_table['index'].append(base_index)
                char_index_table['TreeId'].append(treeId)
                char_index_table['leafId'].append(i)

                char_index_table['char'].append(words_list[i][1])
                char_index_table['index'].append(base_index)
                char_index_table['TreeId'].append(treeId)
                char_index_table['leafId'].append(i)
                continue

            ### Special case: '...'
            if words_list[i] == '...':
                #print("special case: " ,words_list[i])
                char_index_table['char'].append(words_list[i][0])
                char_index_table['index'].append(base_index)
                char_index_table['TreeId'].append(treeId)
                char_index_table['leafId'].append(i)

                char_index_table['char'].append(words_list[i][1])
                char_index_table['index'].append(base_index+2)
                char_index_table['TreeId'].append(treeId)
                char_index_table['leafId'].append(i)

                char_index_table['char'].append(words_list[i][2])
                char_index_table['index'].append(base_index+4)
                char_index_table['TreeId'].append(treeId)
                char_index_table['leafId'].append(i)
                continue

            #Traverse the word and add char and index to the table
            offset = 0
            for char in words_list[i]:
                char_index_table['char'].append(char)
                char_index_table['index'].append(base_index+offset)
                char_index_table['TreeId'].append(treeId)
                char_index_table['leafId'].append(i)
                offset += 1
            try:
                assert base_index + offset  == int(byte_span[-1])
            except AssertionError:
                if debug:
                    print("Error: ", words_list[i], ", num of bytes in python: " ,offset, ", num of bytes in .mrg: ", end_byte_span-base_index, " ,byte_span: ",  byte_list[i])
                    with open('./log.txt', 'a') as f:
                        f.write(filename+'\n')
                        f.write("Error: "+ str(words_list[i])+ ", num of bytes in python: " +str(offset)+ ", num of bytes in .mrg: "+ str(end_byte_span-base_index)+ " ,byte_span: "+  str(byte_list[i])+'\n')

        treeId += 1
    return char_index_table

#Generate sentence from byte index table
def get_sentence_from_byte_index_table(path_to_raw, filename, start, end, debug=False):
    filename = path_to_raw+filename[4:6]+"/"+filename[:8]+'.mrg'
    char_index_table = get_char_index_table(filename, debug=debug)
    sentence = ''
    last_index = -1
    # last_treeId = -1
    for i in range(len(char_index_table['index'])):
        if char_index_table['index'][i] >= start and char_index_table['index'][i] <= end-1:
            # curr_treeId = char_index_table['TreeId'][i]
            curr_index = char_index_table['index'][i]
            if last_index != -1 and last_index+1 != curr_index:
                # print(curr_index)
                # print(last_index)
                sentence += (curr_index - last_index-1)*' '

            last_index = curr_index
            sentence += char_index_table['char'][i]
    return sentence



class annotated_data:
	def __init__(self, line_list):
		# with PDTB Annotation Manual Section 8
		self.type = line_list[0]
		self.conn_spanList = line_list[1].split(';')
		self.conn_src = line_list[2]
		self.conn_type = line_list[3]
		self.conn_pol = line_list[4]
		self.conn_det = line_list[5]
		self.conn_feat_spanList = line_list[6].split(';')
		self.conn1 = line_list[7]
		self.SClass1A = line_list[8]
		self.SClass1B = line_list[9]
		self.conn2 = line_list[10]
		self.SClass2A = line_list[11]
		self.SClass2B = line_list[12]
		self.sup1_spanList = line_list[13].split(';')
		self.arg1_spanList = line_list[14].split(';')
		self.arg1_src = line_list[15]
		self.arg1_type = line_list[16]
		self.arg1_pol = line_list[17]
		self.arg1_det = line_list[18]
		self.arg1_feat_spanList = line_list[19].split(';')
		self.arg2_spanList = line_list[20].split(';')
		self.arg2_src = line_list[21]
		self.arg2_type = line_list[22]
		self.arg2_pol = line_list[23]
		self.arg2_det = line_list[24]
		self.arg2_feat_spanList = line_list[25].split(';')
		self.sup2_spanList = line_list[26].split(';')
		self.adju_reason = line_list[27]
		self.adju_disagr = line_list[28]
		self.PB_Role = line_list[29]
		self.PB_Verb = line_list[30]
		self.Offset = line_list[31]
		self.provenance = line_list[32]
		self.link = line_list[33]
	def get_span_list(list_string):
		span_list = []
		span_list = list_string.split(';') 
		return span_list
	def toStr(self):
	#split with '|'
		return self.type + '|' + ';'.join(self.conn_spanList) + '|' + self.conn_src + '|' + self.conn_type + '|' + self.conn_pol + '|' + self.conn_det + '|' + ';'.join(self.conn_feat_spanList) + '|' + self.conn1 + '|' + self.SClass1A + '|' + self.SClass1B + '|' + self.conn2 + '|' + self.SClass2A + '|' + self.SClass2B + '|' + ';'.join(self.sup1_spanList) + '|' + ';'.join(self.arg1_spanList) + '|' + self.arg1_src + '|' + self.arg1_type + '|' + self.arg1_pol + '|' + self.arg1_det + '|' + ';'.join(self.arg1_feat_spanList) + '|' + ';'.join(self.arg2_spanList) + '|' + self.arg2_src + '|' + self.arg2_type + '|' + self.arg2_pol + '|' + self.arg2_det + '|' + ';'.join(self.arg2_feat_spanList) + '|' + ';'.join(self.sup2_spanList) + '|' + self.adju_reason + '|' + self.adju_disagr + '|' + self.PB_Role + '|' + self.PB_Verb + '|' + self.Offset + '|' + self.provenance + '|' + self.link


def get_meaning_of_index(index):
	if index == 0:
		return "type"
	elif index == 1:
		return "conn_spanList"
	elif index == 2:
		return "conn_src"
	elif index == 3:
		return "conn_type"
	elif index == 4:
		return "conn_pol"
	elif index == 5:
		return "conn_det"
	elif index == 6:
		return "conn_feat_spanList"
	elif index == 7:
		return "conn1"
	elif index == 8:
		return "SClass1A"
	elif index == 9:
		return "SClass1B"
	elif index == 10:
		return "conn2"
	elif index == 11:
		return "SClass2A"
	elif index == 12:
		return "SClass2B"
	elif index == 13:
		return "sup1_spanList"
	elif index == 14:
		return "arg1_spanList"
	elif index == 15:
		return "arg1_src"
	elif index == 16:
		return "arg1_type"
	elif index == 17:
		return "arg1_pol"
	elif index == 18:
		return "arg1_det"
	elif index == 19:
		return "arg1_feat_spanList"
	elif index == 20:
		return "arg2_spanList"
	elif index == 21:
		return "arg2_src"
	elif index == 22:
		return "arg2_type"
	elif index == 23:
		return "arg2_pol"
	elif index == 24:
		return "arg2_det"
	elif index == 25:
		return "arg2_feat_spanList"
	elif index == 26:
		return "sup2_spanList"
	elif index == 27:
		return "adju_reason"
	elif index == 28:
		return "adju_disagr"
	elif index == 29:
		return "PB_Role"
	elif index == 30:
		return "PB_Verb"
	elif index == 31:
		return "Offset"
	elif index == 32:
		return "provenance"
	elif index == 33:
		return "link"


def read_annotated_file(filename):
	'''
	Read gold file from PDTB-3.0-version2 and return a list of annotated data
	
	'''
	lines = []
	with open(filename, 'r') as f:
		for line in f:
			lines.append(line)

	lines = [line.split('|') for line in lines]

	datas = []
	for line in lines:
		# Assert(len(line) == 34)
		data = annotated_data(line)
		data.type = line[0]
		datas.append(data)
	return datas


### lists all implicit discourse relations whose sense is either Contrast or a form of Concession
def get_implicit_contrast_or_consession(datas):
    implicit_contrast_or_consession = [] 
    for data in datas:
        if data.type == 'Implicit' and ('Comparison.Contrast' in data.SClass1A+data.SClass1B or 'Comparison.Concession' in data.SClass1A+data.SClass1B):
            implicit_contrast_or_consession.append(data)
    return implicit_contrast_or_consession

#ToDo: Assert the number of data same to the file given by Bonnie

# check if arg2 occurs in the middle of arg1
def delete_data_if_arg2_in_the_middle_of_arg1(datas):
    arg2_not_in_the_middle_of_arg1 = []
    for data in datas:
        #both span list are not empty
        if data.arg1_spanList!=[''] and data.arg2_spanList!=['']:
            #get the span number of arg1 and arg2
            arg1_span = []
            for span_str in data.arg1_spanList:
                if span_str!='':
                    span = span_str.split('..')
                    for s in span:
                        arg1_span.append(int(s))
            arg2_span = []
            for span_str in data.arg2_spanList:
                if span_str!='':
                    span = span_str.split('..')
                    for s in span:
                        arg2_span.append(int(s))
            #if arg2 not occurs in the middle of arg1
            if not(min(arg2_span) > min(arg1_span) and max(arg2_span) < max(arg1_span)):
                arg2_not_in_the_middle_of_arg1.append(data)
            else:
                # print('arg2 occurs in the middle of arg1')
                # print (data.arg1_spanList)
                # print (data.arg2_spanList)
                continue
    return arg2_not_in_the_middle_of_arg1


def get_preposed_NPs_PPs_byte_spans_from_tree(tree):
    bps_byte_spans =[]
    for node in tree:
        if type(node) is ParentedTree:
            # if node.label() != 'ROOT':
            if (node.label().startswith('NP-') or node.label().startswith('PP-') or node.label().startswith('PP{') or node.label().startswith('NP{'))and 'NP-SBJ' not in node.label():
                #check it's parent is not NP
                curr_cursor_node = node.parent()
                while not(curr_cursor_node is None) and curr_cursor_node.label().split('{')[0] in string.punctuation:
                #if this node is punctuation, then check the previous node
                        # print(curr_cursor_node.label())
                        curr_cursor_node = curr_cursor_node.parent()
                        # print('curr_cursor-1')
                if  not(curr_cursor_node is None) and (curr_cursor_node.label().startswith('S-') or curr_cursor_node.label().startswith('S{')or curr_cursor_node.label().startswith('SINV')):
                    # print('pass2 '+curr_cursor_node.label())
                    #if the last child of the node is S, then this node is preposed
                    if node.label().split('{')[1].split('}')[0].split('.')[0] != node.label().split('{')[1].split('}')[0].split('.')[-1]:#if the span is not a single span
                        # print('pass3 '+node.label())
                        bps_byte_spans.append(node.label().split('{')[1].split('}')[0])
            bps_byte_spans += get_preposed_NPs_PPs_byte_spans_from_tree(node)
        # else:
        #     # print ("Word:", node)
    return bps_byte_spans

def get_preposed_NPs_PPs_byte_spans_from_trees(filename):
    bps_byte_spans =[]
    trees = read_tree(filename)#end with .mrg
    for tree in trees:
        bps_byte_spans += get_preposed_NPs_PPs_byte_spans_from_tree(tree)
    return bps_byte_spans


#Split the file when the line is start with '#'
class Data:
    def __init__(self):
        self.filename = ''
        self.content = ''
def read_from_candidates(filename):
    datas = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        data = Data()
        #append lines until the next '#' is found
        for line in lines:
            if not line.startswith('#'):

                data.content += line
            else:
                datas.append(data)
                data = Data()
                mrg_filename = line.split('/')[-1]
                data.filename = mrg_filename
    return datas[1:]

#Create a dictionary of filename and tree

def get_filename_tree_dict(datas):
    filename_tree_dict = {}
    for data in datas:
        if data.filename not in filename_tree_dict:
            filename_tree_dict[data.filename] = [ParentedTree.fromstring(data.content)]
            # print (data.filename)
            # print(filename_tree_dict[data.filename])
        else:
            # print(data.filename)
            # print(filename_tree_dict[data.filename])
            filename_tree_dict[data.filename].append(ParentedTree.fromstring(data.content))
        # print(data.filename)
        # print (data.content)
        get_preposed_NPs_PPs_byte_spans_from_tree(ParentedTree.fromstring(data.content))
    return filename_tree_dict

#Create a dictionary of filename and preposed NPs and PPs byte spans
def get_filename_preposed_NPs_PPs_byte_spans_dict(filename_tree_dict):
    filename_preposed_NPs_PPs_byte_spans_dict = {}
    for filename in filename_tree_dict:
        filename_preposed_NPs_PPs_byte_spans_dict[filename] = []
        for tree in filename_tree_dict[filename]:
            filename_preposed_NPs_PPs_byte_spans_dict[filename] += get_preposed_NPs_PPs_byte_spans_from_tree(tree)
    return filename_preposed_NPs_PPs_byte_spans_dict

#get DRel byte spans from the file
def get_DRel_byte_spans_from_file(path_to_gold, file):
    filename = path_to_gold +file[4:6]+"/"+file[:8]
    #if the file is not exist, then record the filename in log file
    if not os.path.isfile(filename):
        if debug:
            with open('./log.txt', 'a') as f:
                f.write("The file is not exist: "+filename+"\n")
                f.write(filename+'\n')
            print("The gold file is not exist for %s" % file)
        return []
    datas = read_annotated_file(filename)
    DRel_datas = delete_data_if_arg2_in_the_middle_of_arg1(get_implicit_contrast_or_consession(datas))
    return DRel_datas


if __name__ == '__main__':
    # Prompt for asking the arguments
    import sys
    path_to_PDTB = sys.argv[1]
    path_to_gold = path_to_PDTB + "/gold/"
    path_to_raw = path_to_PDTB + "/raw/"
    input_path = sys.argv[2]
    # check if there is a output path
    if len(sys.argv) == 4:
        output_path = sys.argv[3]
    else:
        output_path = './full_set_DRels_preposed_constits.txt'
    debug = False
    
    count = 0
    datas = read_from_candidates(input_path)
    filename_tree_dict = get_filename_tree_dict(datas)
    filename_preposed_NPs_PPs_byte_spans_dict = get_filename_preposed_NPs_PPs_byte_spans_dict(filename_tree_dict)

    #if the file exists, then delete this file
    if os.path.isfile(output_path):
        os.remove(output_path)
    
    if debug:
        if os.path.isfile('./log.txt'):
            os.remove('./log.txt')

    for filename in filename_preposed_NPs_PPs_byte_spans_dict.keys():
        DRel_byte_spans = get_DRel_byte_spans_from_file(path_to_gold, filename)
        for DRel_byte_span in DRel_byte_spans:
            satisfied = False
            #get the span number of arg1 and arg2
            arg1_span = []
            for span_str in DRel_byte_span.arg1_spanList:
                if span_str!='':
                    span = span_str.split('..')
                    for s in span:
                        arg1_span.append(int(s))
            arg2_span = []
            for span_str in DRel_byte_span.arg2_spanList:
                if span_str!='':
                    span = span_str.split('..')
                    for s in span:
                        arg2_span.append(int(s))

            # if arg1 is at the right of arg2, i.e. the min of arg1 is large than the max of arg2
            if min(arg1_span) > max(arg2_span) or min(arg2_span) > max(arg1_span):
                #Check if there is any preposed NPs or PPs overlap with arg1
                # print(set(filename_preposed_NPs_PPs_byte_spans_dict[filename]))
                for preposed_NPs_PPs_byte_span in set(filename_preposed_NPs_PPs_byte_spans_dict[filename]):
                    left_span = int(preposed_NPs_PPs_byte_span.split('..')[0])
                    right_span = int(preposed_NPs_PPs_byte_span.split('..')[1])
                    if min(arg1_span) > max(arg2_span):
                        for span_str in DRel_byte_span.arg1_spanList:
                            if span_str!='':
                                if left_span >= int(span_str.split('..')[0]) and right_span <= int(span_str.split('..')[1]):
                                    satisfied = True
                                    break
                    elif min(arg2_span) > max(arg1_span):
                        for span_str in DRel_byte_span.arg2_spanList:
                            if span_str!='':
                                if left_span >= int(span_str.split('..')[0]) and right_span <= int(span_str.split('..')[1]):
                                    satisfied = True
                                    break

                    if satisfied:
                        satisfied = False
                        with open(output_path, 'a') as f:
                            f.write('gold/'+filename[4:6]+'/'+filename[:8]+':')
                            f.write(DRel_byte_span.toStr())
                            f.write("Arg1: ")
                            for span_str in DRel_byte_span.arg1_spanList:
                                f.write(get_sentence_from_byte_index_table(path_to_raw, filename, int(span_str.split('..')[0]), int(span_str.split('..')[1])))
                                if len(DRel_byte_span.arg1_spanList)>1:
                                    f.write('; ')
                            f.write('\n')

                            f.write("Arg2: ")
                            for span_str in DRel_byte_span.arg2_spanList:
                                f.write(get_sentence_from_byte_index_table(path_to_raw, filename, int(span_str.split('..')[0]), int(span_str.split('..')[1])))
                                if len(DRel_byte_span.arg2_spanList)>1:
                                    f.write('; ')
                            f.write('\n')
                            f.write("Preposed NPs or PPs span list: ")
                            f.write(preposed_NPs_PPs_byte_span)
                            f.write('\n')

                            f.write("Preposed NPs or PPs: ")
                            f.write(get_sentence_from_byte_index_table(path_to_raw, filename, int(preposed_NPs_PPs_byte_span.split('..')[0]), int(preposed_NPs_PPs_byte_span.split('..')[1])))
                            f.write('\n')
                        count += 1
                        
            else:
                if debug:
                    #Write to log file
                    with open('./log.txt', 'a') as f:
                        f.write('##### arg1 and arg2 overlap in file: '+filename+'\n')

                        f.write('arg1: '+ str(DRel_byte_span.arg1_spanList)+'\n')
                        f.write('arg2: '+ str(DRel_byte_span.arg2_spanList) +'\n')
                        #Write every features in DRel_byte_span split with '|'
                        f.write(DRel_byte_span.toStr()+'\n')
                        print("overlap")
    print('#####  Finished!')
    print('Total number of DRel: '+str(count))
    print("Please check the output file: "+output_path)
    if debug:
        print("Please check the log file: ./log.txt")

        