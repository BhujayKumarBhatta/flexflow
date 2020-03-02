

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