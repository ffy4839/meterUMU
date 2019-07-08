import re
import pandas as pd

model_dict = {
            'G1.6':'02', 'G2.5':'03', 'G4.0':'04',
            'G4':'04', 'G6.0':'05','G6':'05',
            'G10':'06', 'G10.0':'06', 'G16':'07',
            'G16.0':'07','G25':'08','G25.0':'08',
            'G40':'09', 'G40.0':'09', 'G65':'0A',
            'G65.0':'0A','G4.0P': '0B', 'G4P': '0B',
        }
p = [i for i in model_dict.keys() if '.' in i]
print(p)





