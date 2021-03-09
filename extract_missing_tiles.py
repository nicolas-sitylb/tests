# -*- coding: utf-8 -*-

# Author Nicolas Blanc@SITYLB

def extract_missing_tiles():
    
    file_all = 'tuiles_swissimages_nord_vaudois.csv'
    #file_existing = 'ortho.csv'
    #file_existing = 'lidar.csv'
    file_existing = 'mnt.csv'
    
    with open(file_existing) as fe, open(file_all) as fa:
        data_fa = fa.readlines()
        dataFe = fe.read()

    data_fa = [row_fa.strip('\n') for row_fa in data_fa]
    
    matchings = [row_fa for row_fa in data_fa if row_fa.replace('_','-') in dataFe]
    missings = [row_fa.replace('_','-') for row_fa in data_fa if row_fa.replace('_','-') not in dataFe]
        #template = "https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_{}/swissimage-dop10_2020_{}_0.1_2056.tif"
    #template = "https://data.geo.admin.ch/ch.swisstopo.swisssurface3d/swisssurface3d_2015_{}/swisssurface3d_2015_{}_2056_5728.las.zip"
    template = "https://data.geo.admin.ch/ch.swisstopo.swissalti3d/swissalti3d_2019_{}/swissalti3d_2019_{}_0.5_2056_5728.tif"

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
