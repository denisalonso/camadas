# print(bin(b'\xAF'[0]))

msg = 'oi, sou uma string! vamos ver minha conversão em bytes.'
# print(bytes([280]))

# 280 = 0x118

x = 0xFFFFFF

# print(bytes([0x118 & 0xFF]))

print(x & 0xF)
print(x & 0xFF)
print(x & 0xFFF)
print(x & 0xFFFF)
print(x & 0xFFFFF)
print(x & 0xFFFFFF)
print(x & 0xFFFFFFF)