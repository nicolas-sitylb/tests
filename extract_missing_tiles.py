# -*- coding: utf-8 -*-

# Author Nicolas Blanc@SITYLB

def extract_missing_tiles():
    
    file_all = 'tuiles_swissimages_nord_vaudois.csv'
    file_existing = 'ortho.csv'
    
    with open(file_existing) as fe, open(file_all) as fa:
        data_fe = fe.readlines()
        data_fa = fa.readlines()

    with open(file_existing) as fe:
        dataFe = fe.read()

    data_fe = [row_fe.replace('-', '_') for row_fe in data_fe]
    data_fa = [row_fa.strip('\n') for row_fa in data_fa]
    
    matchings = [row_fa for row_fa in data_fa if row_fa.replace('_','-') in dataFe]
    missings = [row_fa.replace('_','-') for row_fa in data_fa if row_fa.replace('_','-') not in dataFe]
    template = "https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_{}/swissimage-dop10_2020_{}_0.1_2056.tif"

    missing_urls = []
    if len(missings)+len(matchings) != len(data_fa):
        print("Error: sums of missing + matchings doesnt equals the length of the input data set!")
    else:
        print("Success!")
        missing_urls = [template.format(missing, missing) for missing in missings]
        with open('missing_tile_urls.csv', 'w') as f:
            for l in missing_urls:
                f.write(f"{l}\n")

    return missing_urls
