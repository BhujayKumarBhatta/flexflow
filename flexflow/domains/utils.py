import itertools


def convert_data_values_as_per_conf(ctype, data:dict, k, v):
    if ctype == 'int' and not isinstance(v, int):
        v = int(v)
        data.update({k: v})
        print('data type converted', data)
    if ctype == 'str'and not isinstance(v, str): 
        v = str(v)
        data.update({k: v})
        print('data type converted', data)
    #if ctype == 'date' and not isinstance(v, date): convert to str
    #if ctype == 'date' and  isinstance(v, str): check dd-mm-yyyy format
    

def lower_case_keys(input_dict):
        lower_key_dict = {}
        for k, v in input_dict.items():
            lowerk = k.lower()
            lower_key_dict.update({lowerk: v})
        return lower_key_dict
    
def convert_dict_in_lod_with_lower_key(lod):
    return [lower_case_keys(d) for d in lod]


def sanitize_input_dict( input_dict):        
    for k, v in input_dict.items():
        if isinstance(v, str):
            v = v.strip()
            #print(v)
            v = v.replace(" ", "_")
            #print('v after replace', v)
            input_dict.update({k: v})
    return input_dict

def sanitize_lod(lod):
    return [sanitize_input_dict(d) for d in lod]


def _compare_two_lists_for_any_element_match(list1, list2):
    result = False
    cartesian_product = itertools.product(list1, list2)              
    role_matched_result = list(map(lambda x: x[0] == x[1], cartesian_product))
    if any(role_matched_result): result = True
    return result
            