def fix_json_array(obj, attr):
    arr = getattr(obj, attr)
 
    if isinstance(arr, list) and len(arr) > 1 and arr[0] == '{':
        
        arr = arr[1:-1]
        arr = ''.join(arr).split(",")
        setattr(obj,attr, arr)
        