# -*- coding: utf-8 -*-
#@author :SHUBHAM SHARMA
#This script is covered under GNU AGPL License
#This script deals with download of planet labs data 
#At present it is downloading the  October 2020 mosaics of planetlabs under NICFI program
#The script requires bounding boxes of each Tehsil/Taluka for Indian Region
#To download the data the user requires Planet API key which must be specified,otherwise the data will not get downloaded.


import os
import json
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from pathlib import Path

def download():
    
    # Path where data will be downloaded
    main_path=os.getenv("DATA")
    csv=os.getenv("CSV")
    
    # API Key
    PLANET_API_KEY = os.getenv("PLANET_API_KEY")
    
    
    item_type = "PSScene4Band"
    
    
    
    
    search_result = \
      requests.get(
        'https://api.planet.com/basemaps/v1/mosaics',
        auth=HTTPBasicAuth(PLANET_API_KEY,''))
        
    #assert search_result.status_code==200
    
    result=search_result.json()
    
    #bbox coordinates
    # Maharashtra
    # lx=72.6
    # ly=15.6
    # ux=80.8
    # uy=22.0
    
    # #Indapur
    # lx=74.6
    # ly=17.8
    # ux=75.1
    # uy=18.3
    
    f_date=result['mosaics'][8]['first_acquired']
    e_date=result['mosaics'][8]['last_acquired']
    
    bbox=pd.read_csv(csv+'csv_test.csv',index_col=False)
    #bbox=bbox[(bbox['Taluka']=='Akole') | (bbox['Taluka']=='Igatpuri')]
    
    clist=[]              #all titles list
    quad_list=[]          #Non overlapping titles
    for row in bbox.iterrows():
        
        taluk=row[1]['Taluka']
        print('Taluka is {}'.format(taluk))
        
        lx=row[1]['lx']
        ly=row[1]['ly']
        ux=row[1]['ux']
        uy=row[1]['uy']
        
        quad=result['mosaics'][8]['_links']['quads']
        quad=quad.replace('lx','').replace('ly','').replace('ux','').replace('uy','').format(lx,ly,ux,uy)
        
        search_result2 = \
        requests.get(
        quad,
        auth=HTTPBasicAuth(PLANET_API_KEY,''))
    
        
    
        quad_result=search_result2.json()
        
        if os.path.exists(os.path.join(main_path,taluk))==False:
                #os.mkdir(os.path.join(main_path,taluk))
                fpath=Path(os.path.join(main_path,taluk)) 
                fpath.mkdir(parents=True, exist_ok=True)       
             
        print(len(quad_result['items']))        
        for i in range(len(quad_result['items'])):
            
            download=quad_result['items'][i]['_links']['download']
            dat_id=quad_result['items'][i]['id']
            
            
            clist.append(dat_id)
            
                    
            if dat_id not in quad_list:
                
                print(dat_id)
                
                response=requests.get(download,auth=HTTPBasicAuth(PLANET_API_KEY,''))
                assert response.status_code==200
                title=response.headers['content-disposition'].split('=')[1].strip('"')
                
                open(os.path.join(main_path,taluk,title),'wb').write(response.content)  
                quad_list.append(dat_id)
                
            else:
                print("Duplicate id{} ".format(dat_id))
            
            
        
    ############# Metadata editing in the files (OPTIONAL) ###################################       
    """    
     
    #edit_path contains the path of gdal_edit.py file
    #Change these paths for metadata change
    #Directory structure example
    #-D:
    #--planet_data
    #---folder with Taluka name
    #----data in the form of tif files
    edit_path='PATH WHERE gdal_edit.py is located'
    #directory where the Planet data is stored
    filedir=''
    from os import path
    from subprocess import Popen,PIPE
    c=0
    
    assert os.listdir(filedir)!=[]
    
    #Changing meta_data of the planet data (optional)
    
    for j in os.listdir(filedir):
        
        fdir=os.path.join(filedir,j)
        
        if len(os.listdir(fdir))!=0:
            print("{} is not empty".format(j))
            
            
            for i in os.listdir(fdir):
                
                
                cmd1 = ['python',path.normpath(edit_path),path.normpath(fdir+"\\"+i),'-mo','MOSAIC_START_DATE={}'.format(f_date),'-mo','MOSAIC_END_DATE={}'.format(e_date)]
                process = Popen(cmd1, stdout=PIPE, stderr=PIPE)
                print(process.communicate())
                c+=1
                print("Counter : {}".format(c))
                
        else:
            print("{} empty".format(j))
            
    """
            
    return [search_result.status_code,response.status_code]
            
def test_m():
    assert download()==[200,200]# Will report other status-code is file not found
    
           