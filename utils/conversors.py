

def hexdump(array):
    return ''.join(["%0.2x" % x for x in array])[0:(2*len(array))]            

def stringToBin(array):
    return [ bin(ch)[2:].zfill(8) for ch in array ]
        
        
