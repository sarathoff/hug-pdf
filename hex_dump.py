import binascii

with open(r"d:\pdf\.env", 'rb') as f:
    data = f.read(500)
    print(binascii.hexlify(data, ' '))
