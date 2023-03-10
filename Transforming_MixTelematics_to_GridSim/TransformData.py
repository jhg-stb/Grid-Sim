import os
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET
from tqdm import tqdm
from operator import itemgetter
import numpy as np
import csv


def _generate_traces(traces_dir: Path):
    # For each file, identify the vehicle_id corresponding to it and the
    # start-date of the file's data.
    original_files = sorted([*traces_dir.joinpath('Original').glob('*.csv')])

    # For each vehicle_id:
    for original_file in tqdm(original_files):
        output_file = traces_dir.joinpath('Processed', original_file.name)
        # Write the header row.
        header_row = ("Date,Time,Latitude,Longitude,Altitude,Speed")
        output_file.parent.mkdir(parents=True, exist_ok=True)
         # For each file in files_of_vehicle:
        with open(original_file, 'r') as f_in:
            # Read and discard the header row.
            reader = csv.reader(f_in)
            header = next(reader)
            # For each remaining row in the file:
            with open(output_file, 'w') as f_out:
                f_out.write(header_row + '\n')
                
                
                for row in reader:
                    date_and_time = row[1]
                    latitude = row[2]
                    longitude = row[3]
                    altitude = row [4]
                    speed = row[10]

                    year = date_and_time[0]+date_and_time[1]+date_and_time[2]+date_and_time[3]
                    month = date_and_time[5]+date_and_time[6]
                    day = date_and_time[8]+date_and_time[9]

                    

                    if (date_and_time[20]=='P'):
                        
                        if (date_and_time[11]+date_and_time[12])=='12':
                            hour = date_and_time[11]+date_and_time[12]
                            minute = date_and_time[14]+date_and_time[15]
                            second = date_and_time[17]+date_and_time[18]
                        else:
                            #Add 12 hours to the hour
                            #hour = int(date_and_time[11]+date_and_time[12])
                            #hour = hour+12
                            #hour = str(hour)
                            hour = str(int(date_and_time[11]+date_and_time[12])+12)
                            minute = date_and_time[14]+date_and_time[15]
                            second = date_and_time[17]+date_and_time[18]
                    
                    elif (date_and_time[20]=='A'):
                        if (date_and_time[11]+date_and_time[12])=='12':
                            hour = '00'
                            minute = date_and_time[14]+date_and_time[15]
                            second = date_and_time[17]+date_and_time[18]
                        else:
                            hour = date_and_time[11]+date_and_time[12]
                            minute = date_and_time[14]+date_and_time[15]
                            second = date_and_time[17]+date_and_time[18]

                    


                    line = "{}-{}-{},{}:{}:{},{},{},{},{}".format(year,month,day,hour,minute,second,latitude,longitude,altitude,speed) + "\n"
                    f_out.write(line)







def main(scenario_dir: Path):
    # Create a list of csv files found in the traces directory.
    
    #scenario_dir = os.getcwd()
    _generate_traces(scenario_dir)
    



if __name__ == '__main__':
    scenario_dir = Path(os.path.abspath(__file__)).parents[0]  # XXX This isn't working when pdb is loaded...
    main(scenario_dir)


