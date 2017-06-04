# -*- coding: utf-8 -*-

def represents_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False