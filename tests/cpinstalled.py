import sys
print("[TESTS] --> Checking for cursesplus")
try:
    import cursesplus
    print("[TESTS] --> Found cursesplus")
except:
    print("[TESTS] --> Falied to find cursesplus")
    sys.exit(-1)