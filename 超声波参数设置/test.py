

a = '68 AB 57 58 AA AA AA AA AA 12 34 56 78 90 A1 00 1A 90 0F 01 00 00 06 00 12 D6 80 00 00 00 00 00 00 00 00 01 00 01 05 19 07 08 17 C7 16'.replace(' ','')
print(a[-12:-4])


for i in range(0,len(a),2):
    if 'D6' == a[i:i+2]:
        print(i)


