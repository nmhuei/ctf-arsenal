#!/usr/local/bin/python3
flag = open('flag.txt').read()
while True:
    try:
        flag = input('format: ').format(flag)
    except:
        break
