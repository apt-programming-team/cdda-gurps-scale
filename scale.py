import json
from operator import itemgetter
from pprint import pprint

with open('cdda_data/armor.json') as f:
    data = json.load(f)
with open('cdda_data/materials.json') as g:
    materials = json.load(g)
    
#Get a list of all possible materials
armor_materials = []
for i in range(len(data)):
    for j in range(len(data[i]['material'])):
        if data[i]['material'][j] not in armor_materials and len(data[i]['material'][j]) > 1:
            armor_materials.append(data[i]['material'][j])

armor_thicknesses = {key: None for key in ['cloak', 'armor_larmor', 'armor_chitin', 'chainmail_suit', 'cuirass_lightplate', 'armor_plate', 'kevlar']}
armors = []
for i in range(len(data)):
    if data[i]["id"] in armor_thicknesses:
        armor_thicknesses[data[i]["id"]] = data[i]["material_thickness"]
        armors.append(data[i])

material_obj = {key: None for key in ['br', 'cr', 'acid_r', 'fire_r', 'elec_r', 'chip_r']}
material_info = {key: None for key in armor_materials}
for material in armor_materials:
    for i in range(len(materials)):
        if material == materials[i]['ident']:
            material_obj['br'] = materials[i]['bash_resist']
            material_obj['cr'] = materials[i]['cut_resist']
            material_obj['acid_r'] = materials[i]['acid_resist']
            material_obj['fire_r'] = materials[i]['fire_resist']
            material_obj['elec_r'] = materials[i]['elec_resist']
            material_obj['chip_r'] = materials[i]['chip_resist']
    material_info[material] = material_obj

known_DRs = {key: None for key in ['cotton', 'leather', 'chitin', 'iron', 'steel', 'kevlar']}
known_DRs['cotton'] = 1
known_DRs['leather'] = 2
known_DRs['chitin'] = 3
known_DRs['iron'] = 5
known_DRs['steel'] = 5
known_DRs['kevlar'] = 8
SFs = {key: None for key in ['cotton', 'leather', 'chitin', 'iron', 'steel', 'kevlar']}
for known in known_DRs:
    obj = material_info[known]
    sf = (known_DRs[known])/(obj['br'] + obj['cr'])
    SFs[known] = sf

for armor in armors:
    if len(armor["material"]) == 1:
        SFs[armor["material"][0]] /= armor["material_thickness"]

SFs['iron'] = known_DRs['iron'] - ((material_info['iron']['br']+ material_info['iron']['br']) * armor_thicknesses['armor_plate'] * SFs['leather'])
SFs['iron'] /= ((material_info['iron']['br'] + material_info['iron']['cr']) * armor_thicknesses['armor_plate'])
SFs['steel'] = known_DRs['steel'] - ((material_info['steel']['br']+ material_info['steel']['br']) * armor_thicknesses['cuirass_lightplate'] * SFs['leather'])
SFs['steel'] /= ((material_info['steel']['br'] + material_info['steel']['cr']) * armor_thicknesses['cuirass_lightplate'])

avg_SF = 0
for sf in SFs:
    avg_SF += SFs[sf]

avg_SF /= len(SFs)

#weight scale is in kg, multiply by 2.2 to get pounds

out = []
for i in range(len(data)):
    out.append({key: None for key in ['name', 'desc', 'dr', 'acid_r', 'fire_r', 'elec_r', 'cost', 'weight', 'volume', 'misc']})
    out[i]['name'] = data[i]['name']
    out[i]['desc'] = data[i]['description']
    out[i]['cost'] = data[i]['price'] / 100
    out[i]['weight'] = int(data[i]['weight'] * 2.2 / 1000)
    out[i]['volume'] = data[i]['volume']
    if 'flags' in data[i]:
        out[i]['misc'] = data[i]['flags']
    out[i]['dr'] = -1
    out[i]['acid_r'] = -1
    out[i]['fire_r'] = -1
    out[i]['elec_r'] = -1
    j = 1
    for material in data[i]['material']:
        if material in armor_materials:
            if 'material_thickness' in data[i]:
                out[i]['dr'] += (material_info[material]['br'] + material_info[material]['cr'])*data[i]['material_thickness']*avg_SF
            else:
                out[i]['dr'] += (material_info[material]['br'] + material_info[material]['cr'])*1*avg_SF
            out[i]['acid_r'] = out[i]['acid_r'] + material_info[material]['acid_r'] / j
            out[i]['fire_r'] = out[i]['fire_r'] + material_info[material]['fire_r'] / j
            out[i]['elec_r'] = out[i]['elec_r'] + material_info[material]['elec_r'] / j
        j += 1

with open('gurps_data/scaled_armor.json', 'w') as h:
    json.dump(out, fp=h, indent = 2, sort_keys=True, ensure_ascii=False)

