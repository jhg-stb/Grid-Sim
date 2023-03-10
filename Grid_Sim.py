import os
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET
from tqdm import tqdm
from operator import itemgetter
import numpy as np
import csv
import shutil
import geopy.distance
from geopy.distance import geodesic as GD
import matplotlib.pyplot as plt
import warnings

# Ignore the mean of empty slice warning
warnings.filterwarnings("ignore", category=RuntimeWarning)

#Radius of charging station inaccurary
charging_radius = 100
Batterty_Flat = False

delete_folders = True
initialise_done = False
prep_done = False
todays_mobility_data = {}
VehiclesDF = {}
ChargingStationsDF = {}

number_of_vehicles = 0
same_battery_cap = 0
standard_battery_capacity = 0


class TempVehicleClass:
    def __init__(self, name, battery_capacity, efficiency):
        self.name = name
        self.battery_capacity = battery_capacity
        self.efficiency = efficiency
TempVehicles = []

class TempChargingStationClass:
    def __init__(self, name, lat, lon, number_of_chargers, charging_power):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.number_of_chargers = number_of_chargers
        self.charging_power = charging_power
TempChargingStations = []

class VehicleClass:
    def __init__(self, name, battery_capacity, efficiency, vehicle_active,latitude,longitude,altitude,speed,battery_status,where_charging):
            self.name = name
            self.battery_capacity = battery_capacity
            self.efficiency = efficiency
            self.vehicle_active = vehicle_active
            self.latitude = latitude
            self.longitude = longitude
            self.altitude = altitude
            self.speed = speed
            self.battery_status = battery_status
            self.where_charging = where_charging
Vehicles = []

class ChargingStationClass:
    def __init__(self, name, lat, lon, number_of_chargers, charging_power,available_chargers,chargers_active,energy_delivered,daily_energy_delivered):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.number_of_chargers = number_of_chargers
        self.charging_power = charging_power
        self.available_chargers = available_chargers
        self.chargers_active = chargers_active
        self.energy_delivered = energy_delivered
        self.daily_energy_delivered = daily_energy_delivered
ChargingStationsObj = []
ChargingStations = []



def initialise_vehicles(Scenario_path):


    #Ask how many vehicles the user wants to have as input
    selection = input('\nHow many vehicles do you want to use as input?  ')
    selection = int(selection)+1


    #Establish if the user wants to input the vehicle parameters now or later
    vehicle_input_option = input('\nDo you want to input vehicle parameters now or later enter directly into the designated document?\n1. Now \n2. Later In Document \n')
    while not (vehicle_input_option=='1' or vehicle_input_option=='2'):
        vehicle_input_option = input('\nInvalid option. Please enter a valid option: ')


    
    if vehicle_input_option == '1':

        #Ask if they want to name the vehicles
        vehicle_name_option = input('\nDo you want to name the vehicle(s)?\nNOTE: This can be done at a later stage by editing the folder name in <Input\Vehicles>\n1. Yes \n2. No\n')
        while not (vehicle_name_option=='1' or vehicle_name_option=='2'):
            vehicle_name_option = input('\nInvalid option. Please enter a valid option: ')


        if vehicle_name_option=='1':
            for i in range(1,selection):
                vehicle_name = input('\nPlease name vehicle #' +str(i)+': ')
                TempVehicles.append(TempVehicleClass(vehicle_name,None, None))

        if vehicle_name_option=='2':
            for i in range(1,selection):
                TempVehicles.append(TempVehicleClass('Vehicle_'+str(i),None, None))

        #CREATE FOLDERS WITH VEHICLE'S NAME
        for obj in TempVehicles:
            Newfolder = obj.name
            os.makedirs(Newfolder)


        #Define if all vehicles has the same battery capacity
        if selection != 2:
            same_battery_cap = input('\nDoes all the vehicles have the same battery capcaity?\n1. Yes \n2. No \n')
            while not (same_battery_cap=='1' or same_battery_cap=='2'):
                same_battery_cap = input('\nInvalid option. Please enter a valid option: ')
        else:
            same_battery_cap = '1'

        #All vehicles has the same battery capacity
        if same_battery_cap == '1':
            standard_battery_capacity = input('\nPlease enter the battery capacity in [kWh]:  ')
            for obj in TempVehicles:
                obj.battery_capacity = standard_battery_capacity

            

        #Each vehicle has a unique battery capacity
        if same_battery_cap == '2':
            print('\nPlease enter the individual battery capacity of each vehicle.')
            for obj in TempVehicles:
                individual_battery_cap = input(obj.name + ': ')
                obj.battery_capacity = individual_battery_cap
                

        
        #Establish if the user wants to use a standard kWh/km, or is going to input energy usage information
        changing_efficiency = input('\nDo you want to use a constant kWh/km efficiency rate, or input energy usage as part of mobility data?\n1. Constant kWh/km \n2. Mobility Data kWh/km \n')
        while not (changing_efficiency=='1' or changing_efficiency=='2'):
            changing_efficiency = input('\nInvalid option. Please enter a valid option: ')


        #Constant kWh/km selected
        if changing_efficiency == '1':
            #Establish if each vehicle has a unique efficiency
            if selection!=2:
                unique_efficiency = input('\nDoes each vehicle have a unique efficiency?\n1. Yes \n2. No \n')
                while not (unique_efficiency=='1' or unique_efficiency=='2'):
                    unique_efficiency = input('\nInvalid option. Please enter a valid option: ')
            else:
                unique_efficiency = '2'

            #Each vehicle has a unique efficiency
            if unique_efficiency == '1':
                print('\nPlease enter the individual energy efficiency [in kWh/km] of each vehicle.')
                for obj in TempVehicles:
                    individual_efficiency = input(obj.name+': ')
                    obj.efficiency = float(individual_efficiency)

            #All vehicles has the same efficiency
            if unique_efficiency == '2':
                individual_efficiency = input('\nPlease enter the energy efficiency [in kWh/km]: ')
                for obj in TempVehicles:
                    obj.efficiency = float(individual_efficiency)


        #Changing kWh/km selected
        if changing_efficiency == '2':
            for obj in TempVehicles:
                obj.efficiency = 'N/A'

    if vehicle_input_option == '2':

        #CREATE FOLDERS WITH VEHICLE'S NUMBERS
        #Create a seperate folder for each vehicle
        for i in range (1,selection):
            Newfolder = 'Vehicle_'+str(i)
            os.makedirs(Newfolder)


        for i in range(1,selection):
            name = 'Vehicle_'+ str(i)
            battery_capacity = ''
            efficiency = ''
            TempVehicles.append(TempVehicleClass(name,battery_capacity,efficiency))



    for obj in TempVehicles:
        temp_path = Scenario_path+'\\'+'Input'+'\\'+'Vehicles'+'\\'+obj.name
        os.chdir(temp_path)
        with open('Vehicle_Parameters.csv', 'w') as f_parameters:
            header = ("Battery Capacity [kWh], Energy Efficiency [kWh/km]")
            f_parameters.write(header + '\n')
            line="{},{}".format(obj.battery_capacity,obj.efficiency)
            f_parameters.write(line)

def initialise_charging_stations(Scenario_path):
    #Ask how many charging stations there are
    selection = input('\nHow many charging stations are there? ')
    while  selection == '0':
        selection = input('\n0 is an invalid option. Please enter a valid option. How many charging stations are there? ')
    selection = int(selection)+1


    #Establish if the user wants to input the charging data now or later
    charging_input_option = input('\nDo you want to input charging station information now or later enter directly into the designated document?\n1. Now \n2. Later In Document \n')
    while not (charging_input_option=='1' or charging_input_option=='2'):
        charging_input_option = input('\nInvalid option. Please enter a valid option: ')

    if charging_input_option == '1':

        #Establish if all chargers has the same charging speed/power
        if selection != 2:
            same_charging_speeds = input('\nDoes all the charging stations charge at the same speed?\n1. Yes \n2. No \n')
            while not (same_charging_speeds=='1' or same_charging_speeds=='2'):
                same_charging_speeds = input('\nInvalid option. Please enter a valid option: ')
        else:
            same_charging_speeds = '1'

        #All charging stations have the same speed
        if same_charging_speeds == '1':
            charging_speed_general = input('\nWhat is the charging speed [in kW]? ' )

            for i in range(1,selection):
                name = input('\nName charging station #' + str(i) + ': ')
                lat = input('Latitude [in deg] of ' + name + ': ')
                lon = input('Longitude [in deg] of ' + name + ': ')
                number_of_chargers = input('Number of charging points at ' + name + ': ')
                TempChargingStations.append(TempChargingStationClass(name,lat,lon,number_of_chargers,charging_speed_general))

        #Each charging station has their own speed
        if same_charging_speeds == '2':
            for i in range(1,selection):
                name = input('\nName charging station #' + str(i) + ': ')
                lat = input('Latitude [in deg] of ' + name + ': ')
                lon = input('Longitude [in deg] of ' + name + ': ')
                number_of_chargers = input('Number of charging points at ' + name + ': ')
                charging_speed_individual = input('Charging speed [in kW] of ' + name + ': ' )
                TempChargingStations.append(TempChargingStationClass(name,lat,lon,number_of_chargers,charging_speed_individual))

    if charging_input_option =='2':
        for i in range(1,selection):
            name = 'Charging_Station_'+ str(i)
            lat = '*input value*'
            lon = '*input value*'
            number_of_chargers = '*input value*'
            charging_speed_general = '*input value*'
            TempChargingStations.append(TempChargingStationClass(name,lat,lon,number_of_chargers,charging_speed_general))

    for obj in TempChargingStations:
        temp_path = Scenario_path+'\\'+'Input'+'\\'+'Charging_Stations'
        os.chdir(temp_path)
        file_name = obj.name + '.csv'
        with open(file_name, 'w') as f_parameters:
            header = ("Latitude [deg], Longitude [deg], Number of Chargers, Charging Speed [kW]")
            f_parameters.write(header + '\n')
            line="{},{},{},{}".format(obj.lat,obj.lon,obj.number_of_chargers,obj.charging_power)
            f_parameters.write(line)

def initialise(Scenario_path):
    
    os.chdir(Scenario_path)

    #check scenario path for any folders, ask to clear
    dir = os.listdir(Scenario_path)

    while len(dir)!=0:
        print('\nScenario folder conatins other folders or documents. Please clear the folder.')
        enter = input('Press ENTER once scenario folder has been cleared.')
        if enter == '':
            print('Checking scenario folder. . .')
            dir = os.listdir(Scenario_path)

    

    #Create Input Folder
    Input_folder = 'Input'
    os.makedirs(Input_folder)
    Output_folder = 'Output'
    os.makedirs(Output_folder)

    #Create Output Folder
    path2 = Scenario_path+'\\'+'Input'
    os.chdir(path2)
    os.makedirs('Vehicles')
    os.makedirs('Charging_Stations')

    #Create Vehicles Folder in Input  
    path3 = Scenario_path+'\\'+'Input'+'\\'+'Vehicles'
    os.chdir(path3)

    initialise_vehicles(Scenario_path)
    initialise_charging_stations(Scenario_path)

    
    print('\nScenario folder succesfully created. Populate the Input folders accordingly.\nOnce populated, press ENTER, or rerun Grid-Sim and select option 1.')
    enter = input()


    global initialise_done
    if enter == '':
        initialise_done = True
    else:
        initialise_done = False

def check_if_folders_complete(Scenario_path):

    #Check if Input and Output folders exist
    os.chdir(Scenario_path)
    temp_path = Scenario_path+'\\'+'Input'
    isExist = os.path.exists(temp_path)
    if isExist==False:
        print('\nInput folder not created in scenario directory. Please initialise a scenario for this directory.')
        exit()

    temp_path = Scenario_path+'\\'+'Output'
    isExist = os.path.exists(temp_path)
    if isExist==False:
        print('\nOutput folder not created in scenario directory. Please initialise a scenario for this directory.')
        exit()


    #Check if Vehicles and Chargin Station folders exist 
    temp_path = Scenario_path+'\\'+'Input'+'\\'+'Vehicles'
    isExist = os.path.exists(temp_path)
    if isExist==False:
        print('\Vehicles folder not created in scenario directory. Please populate manually or reinitialise this scenario.')
        exit()

    temp_path = Scenario_path+'\\'+'Input'+'\\'+'Charging_Stations'
    isExist = os.path.exists(temp_path)
    if isExist==False:
        print('\Charging_Stations folder not created in scenario directory. Please populate manually or reinitialise this scenario.')
        exit()


    #Check if Vehicles folder has information
    temp_path = Scenario_path+'\\'+'Input'+'\\'+'Vehicles'
    dir = os.listdir(temp_path)
    if len(dir)==0:
        print('\nNo vehicles have been defined in this scenario. Please populate manually or reinitialise this scenario.')
        exit()

    #Check if Chargin_Stations folder has information
    dir_path = Scenario_path + '\\' + 'Input' + '\\' + 'Charging_Stations'
    files = os.listdir(dir_path)

    if not any(file.endswith('.csv') for file in files):
        print("\nNo charging stations has been defined, or not given in '.csv' format. Please populate manually or reinitialise this scenario.")
        exit()
    print("\nCharging information found in appropriate directory.")

        
    #Check if individual vehicle folders have Mobility_Data.csv and Vehicle_Parameters.csv documents
    dir_path = Scenario_path+'\\'+'Input'+'\\'+'Vehicles'
    folders = [f for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]

    for i in range(len(folders)):
        sub_dir_path = dir_path + '\\' + folders[i]
        files = os.listdir(sub_dir_path)
        if not any([x for x in files if x.startswith('Vehicle_Parameters') and x.endswith('.csv')]):
            print(f"Vehicle_Parameters.csv not found in {folders[i]} directory. Please populate manually or reinitialise this scenario.")
            exit()
            

    print("All Vehicle_Parameters.csv files found in appropriate directories.")

    for i in range(len(folders)):
        sub_dir_path = dir_path + '\\' + folders[i]
        files = os.listdir(sub_dir_path)
        if not any([x for x in files if x.startswith('Mobility_Data') and x.endswith('.csv')]):
            print(f"Mobility_Data.csv not found in {folders[i]} directory. Please populate manually or reinitialise this scenario.")
            exit()
            

    print("All Mobility_Data.csv files found in appropriate directories.")

def downsample_input_data(Scenario_path):
    dir_path = Scenario_path + '\\' + 'Input' + '\\' + 'Vehicles'
    vehicle_folders = [f for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]


    #Create downsample folder in the Output folder
    path2 = Scenario_path+'\\'+'Output'
    os.chdir(path2)
    os.makedirs('Downsampled_Mobility_Data')

    print('\nDownsampling mobility data:')
    for i in tqdm(range(0,len(vehicle_folders))):
        temp_dir = Scenario_path + '\\' + 'Input' + '\\' + 'Vehicles' + '\\' + vehicle_folders[i]
        mobility_data_file = os.path.join(temp_dir, 'Mobility_Data.csv')

        temp_output_directory = Scenario_path + '\\' + 'Output' + '\\' + 'Downsampled_Mobility_Data'
        downsampled_mobility_data_file = os.path.join(temp_output_directory, vehicle_folders[i]+'.csv')

        header_row = ("Date,Time,Latitude,Longitude,Altitude,Speed")
        previous_minute = 'none'
        with open(mobility_data_file, 'r') as f_in:
            csvreader = csv.DictReader(f_in)

            with open(downsampled_mobility_data_file, 'w') as f_out:
                f_out.write(header_row + '\n')


                for row in csvreader:

                    time = row['Time']
                    current_minute = float(time[(len(time)-4)])

                    if current_minute == previous_minute:
                        continue

                    
                    date = row['Date']
                    lat = row['Latitude']
                    lon = row['Longitude']
                    alt = row['Altitude']
                    speed = row['Speed']

                    line = "{},{},{},{},{},{}".format(date,time,lat,lon,alt,speed) + "\n"
                    f_out.write(line)

                    previous_minute = current_minute

def seperate_daily_mobility_data(Scenario_path):
    dir_downsampled_mobility_folderath = Scenario_path + '\\' + 'Output' + '\\' + 'Downsampled_Mobility_Data'
                
    path = Scenario_path+'\\'+'Output'
    os.chdir(path)
    os.makedirs('Daily_Seperated_Downsampled_Mobility_Data')           
            
    downsampled_mobility_data_files = [f for f in os.listdir(dir_downsampled_mobility_folderath) if f.endswith('.csv')]
    header_row = ("Date,Time,Latitude,Longitude,Altitude,Speed")

    print('\nSeperating daily mobility data:')
    for i in tqdm(range(0,len(downsampled_mobility_data_files))):

        temp_dir = Scenario_path + '\\' + 'Output' + '\\' + 'Downsampled_Mobility_Data'
        downsampled_mobility_data_file = os.path.join(temp_dir, downsampled_mobility_data_files[i])


        with open(downsampled_mobility_data_file, 'r') as f_in:
            csvreader = csv.DictReader(f_in)

            previous_day = 'none'
            for row in csvreader:

                date = row['Date']
                day = date[9]

                #Check first if it is a new date

                if day != previous_day: #New day

                    

                    #Check if this date already has a folder due to other vehicles
                    checking_date_folder = Scenario_path + '\\' + 'Output' + '\\' + 'Daily_Seperated_Downsampled_Mobility_Data' + '\\' + date
                    if not (os.path.exists(checking_date_folder)):
                        #Day folder does not exist, create a new one
                        new_path = Scenario_path + '\\' + 'Output' + '\\' + 'Daily_Seperated_Downsampled_Mobility_Data'
                        os.chdir(new_path)
                        os.makedirs(date)
                                    
                    #Create new .csv file dor the day's data in the already existing folder
                    date_directory = Scenario_path + '\\' + 'Output' + '\\' + 'Daily_Seperated_Downsampled_Mobility_Data' + '\\' + date
                    daily_seperated_downsampled = os.path.join(date_directory, downsampled_mobility_data_files[i])

                    with open(daily_seperated_downsampled, 'w') as f_out:
                        f_out.write(header_row + '\n')
                        time = row['Time']
                        lat = row['Latitude']
                        lon = row['Longitude']
                        alt = row['Altitude']
                        speed = row['Speed']
                        line = "{},{},{},{},{},{}".format(date,time,lat,lon,alt,speed) + "\n"
                        f_out.write(line)

                else:
                    date_directory = Scenario_path + '\\' + 'Output' + '\\' + 'Daily_Seperated_Downsampled_Mobility_Data' + '\\' + date
                    daily_seperated_downsampled = os.path.join(date_directory, downsampled_mobility_data_files[i])

                    with open(daily_seperated_downsampled, 'a') as f_out:
                        time = row['Time']
                        lat = row['Latitude']
                        lon = row['Longitude']
                        alt = row['Altitude']
                        speed = row['Speed']
                        line = "{},{},{},{},{},{}".format(date,time,lat,lon,alt,speed) + "\n"
                        f_out.write(line)

                previous_day = day

def fill_missing_minutes(Scenario_path):
    dir_seperated_daily_FOLDERS = Scenario_path + '\\' + 'Output' + '\\' + 'Daily_Seperated_Downsampled_Mobility_Data'

    #Create new folder for filled minutes data
    path = Scenario_path+'\\'+'Output'
    os.chdir(path)
    os.makedirs('Filled_Minutes_Mobility_Data') 


    #Create a list of all the dates
    dates_folders = [f for f in os.listdir(dir_seperated_daily_FOLDERS) if os.path.isdir(os.path.join(dir_seperated_daily_FOLDERS, f))]

    #Output folder directory
    dir_missing_minutes_filled = Scenario_path + '\\' + 'Output' + '\\' + 'Filled_Minutes_Mobility_Data'
    
    print('\nFilling missing minutes for each date:')
    for i in tqdm(range(0,len(dates_folders))):

        #Create a list of all the files within the date folder
        dir_files = Scenario_path + '\\' + 'Output' + '\\' + 'Daily_Seperated_Downsampled_Mobility_Data' + '\\' + dates_folders[i]
        seperated_mobility_data_files = [f for f in os.listdir(dir_files) if f.endswith('.csv')]

        #Create this date's folder in the new directory for filled minutes folder
        os.chdir(dir_missing_minutes_filled)
        os.makedirs(dates_folders[i]) 

        date_directory_filled = Scenario_path + '\\' + 'Output' + '\\' + 'Filled_Minutes_Mobility_Data' + '\\' + dates_folders[i]

        
        for i in range(0,len(seperated_mobility_data_files)):

            seperated_mobility_file = os.path.join(dir_files, seperated_mobility_data_files[i])

            with open(seperated_mobility_file, 'r') as f_in:

                filled_daily_data = os.path.join(date_directory_filled, seperated_mobility_data_files[i]) 
                header_row = ("Date,Minute of Day,Latitude,Longitude,Altitude,Speed")

                reader = csv.reader(f_in)
                header = next(reader)
                first_row = next(reader)

                previous_date = first_row[0] 
                previous_lat = first_row[2]
                previous_lon = first_row[3]
                previous_speed = first_row[5]
                previous_time = first_row[1]
                previous_alt = first_row[4]


                previous_minute = int(previous_time[0]+previous_time[1])*60 + int(previous_time[3]+previous_time[4])

                with open(filled_daily_data, 'w') as f_out:
                    
                    f_out.write(header_row + '\n')
                    line = "{},{},{},{},{},{}".format(previous_date,previous_minute,previous_lat,previous_lon,previous_alt,previous_speed) + "\n"
                    f_out.write(line)

                    for row in reader:
                        time = row[1]
                        minute = int(time[0]+time[1])*60 + int(time[3]+time[4])

                        if previous_minute+1 != minute: #missing minute
                            while True:
                                previous_minute = previous_minute+1
                                speed = 0.0
                                line = "{},{},{},{},{},{}".format(previous_date,previous_minute,previous_lat,previous_lon,previous_alt,speed) + "\n"
                                f_out.write(line)
                                if previous_minute+1 == minute:
                                    break

                        date = row[0]
                        lat = row[2]
                        lon = row[3]
                        alt = row[4]
                        speed = row[5]

                        line = "{},{},{},{},{},{}".format(date,minute,lat,lon,alt,speed)+ "\n"
                        f_out.write(line)

                        previous_lat = lat
                        previous_lon = lon
                        previous_speed = speed
                        previous_minute = minute
                        previous_alt = alt

def extrapolate_24hours(Scenario_path):
    
    dir_filled_seperated_daily_FOLDERS = Scenario_path + '\\' + 'Output' + '\\' + 'Filled_Minutes_Mobility_Data'

    #Create new folder for extrapolated data
    path = Scenario_path+'\\'+'Output'
    os.chdir(path)
    os.makedirs('24h_Extrapolated_Data') 

    #Create a list of all the dates
    dates_folders = [f for f in os.listdir(dir_filled_seperated_daily_FOLDERS) if os.path.isdir(os.path.join(dir_filled_seperated_daily_FOLDERS, f))]


    #Output folder directory
    dir_extrapolated_data = Scenario_path + '\\' + 'Output' + '\\' + '24h_Extrapolated_Data'


    print('\nExtrapolating data over 24hours for each date:')
    for i in tqdm(range(0,len(dates_folders))):

        #Create a list of all the files within the date folder
        dir_files = Scenario_path + '\\' + 'Output' + '\\' + 'Filled_Minutes_Mobility_Data' + '\\' + dates_folders[i]
        filled_mobility_data_files = [f for f in os.listdir(dir_files) if f.endswith('.csv')]

        #Create this date's folder in the new directory for extrapolated data folder
        os.chdir(dir_extrapolated_data)
        os.makedirs(dates_folders[i]) 

        date_directory_extrapolated = Scenario_path + '\\' + 'Output' + '\\' + '24h_Extrapolated_Data' + '\\' + dates_folders[i]

        for i in range(0,len(filled_mobility_data_files)):
            
            filled_mobility_data_file = os.path.join(dir_files, filled_mobility_data_files[i])

            with open(filled_mobility_data_file, 'r') as f_in:

                day_minute_counter = 0

                extrapolated_daily_data = os.path.join(date_directory_extrapolated, filled_mobility_data_files[i]) 
                header_row = ("Date,Minute of Day,Latitude,Longitude,Altitude,Speed")

                reader = csv.reader(f_in)
                header = next(reader)

                with open(extrapolated_daily_data, 'w') as f_out:

                    f_out.write(header_row + '\n')

                    for row in reader:

                        date = row[0]
                        minute = row[1]
                        lat = row[2]
                        lon = row[3]
                        alt = row[4]
                        speed = row[5]

                        while int(minute) != day_minute_counter:
                            speed = '0'
                            line = "{},{},{},{},{},{}".format(date,day_minute_counter,lat,lon,alt,speed)+ "\n"
                            f_out.write(line)
                            day_minute_counter = day_minute_counter + 1

                        line = "{},{},{},{},{},{}".format(date,minute,lat,lon,alt,speed)+ "\n"
                        f_out.write(line)
                        day_minute_counter = day_minute_counter + 1

                    while day_minute_counter != 1440:
                        speed = '0'
                        line = "{},{},{},{},{},{}".format(date,day_minute_counter,lat,lon,alt,speed)+ "\n"
                        f_out.write(line)
                        day_minute_counter = day_minute_counter + 1

def prepare_mobility_files(Scenario_path):
    #Start by downsampling input data to minutely data (remove all second data)
    downsample_input_data(Scenario_path)

    #Seperate each day's downsampled mobility data. Combine different vehicles for the same day
    seperate_daily_mobility_data(Scenario_path)
    #Delete downsampled mobility data. No longer needed
    folder_path = Scenario_path + '\\' + 'Output' + '\\' + 'Downsampled_Mobility_Data'
    if delete_folders == True:
        shutil.rmtree(folder_path)

    #Fill in missing minutes within daily mobility data
    fill_missing_minutes(Scenario_path)
    #Delete seperated mobility data. No longer needed
    folder_path = Scenario_path + '\\' + 'Output' + '\\' + 'Daily_Seperated_Downsampled_Mobility_Data'
    if delete_folders == True:
        shutil.rmtree(folder_path)

    #Complete 24hours for each day for each vehicle
    extrapolate_24hours(Scenario_path)
    folder_path = Scenario_path + '\\' + 'Output' + '\\' + 'Filled_Minutes_Mobility_Data'
    if delete_folders == True:
        shutil.rmtree(folder_path)

def check_and_prepare(Scenario_path):

    check_if_folders_complete(Scenario_path)
    print("All input files found in appropriate directories.")

    prepare_mobility_files(Scenario_path)

    print('\nFiles succesfully prepared for simulation. Please do not edit any Input or Output folders or files.\nWhen ready to run Grid-Sim, press ENTER, or rerun Grid-Sim and select option 2.')
    enter = input()
    
    global prep_done
    if enter == '':
        prep_done = True
    else:
        prep_done = False

def offtake_power(Scenario_path):
    dir_vehicles = Scenario_path + '\\' + 'Input' + '\\' + 'Vehicles'

    path = Scenario_path+'\\'+'Output'
    os.chdir(path)
    os.makedirs('Power_Offtake_Added') 

    vehicle_folders = [f for f in os.listdir(dir_vehicles) if os.path.isdir(os.path.join(dir_vehicles, f))] 

    dir_24h_folders = Scenario_path + '\\' + 'Output' + '\\' + '24h_Extrapolated_Data'
    dates_folders = [f for f in os.listdir(dir_24h_folders) if os.path.isdir(os.path.join(dir_24h_folders, f))]

    global Vehicles
    global VehiclesDF

    #Create folder for each date in new output folder
    path = Scenario_path+'\\'+'Output'+'\\'+'Power_Offtake_Added'
    os.chdir(path)
    for i in range(0,len(dates_folders)):
        os.makedirs(dates_folders[i])


    print('\nCalculating energy expenditure for each vehicle:')
    for i in tqdm(range(0,len(vehicle_folders))):

        path = Scenario_path + '\\' + 'Input' + '\\' + 'Vehicles' + '\\' + vehicle_folders[i]
        vehicle_parameters_file = os.path.join(path, 'Vehicle_Parameters.csv')


        #Create an object for each vehicle
        with open(vehicle_parameters_file, 'r') as f_in:

            reader = csv.reader(f_in)
            header = next(reader)
            first_row = next(reader)

            temp_battery_cap = float(first_row[0])
            temp_efficiency = float(first_row[1])
            temp_name = vehicle_folders[i]


            vehicle =  VehicleClass(temp_name, temp_battery_cap, temp_efficiency, None, None, None, None, None, temp_battery_cap, 'N/A')
            Vehicles.append(vehicle)

        
        VehiclesDF[vehicle_folders[i]] = pd.read_csv(vehicle_parameters_file)
        
        for x in range(0, len(dates_folders)):

            #Check if there is a mobility file for this vehicle in the specific date
            vehicle_file_check = Scenario_path + '\\' + 'Output' + '\\' + '24h_Extrapolated_Data'+ '\\' + dates_folders[x] + '\\' + temp_name + '.csv'
            
            #There is a 24h extrapolated mobility file in this date for this vehicle
            if os.path.exists(vehicle_file_check):


                folder_path = Scenario_path+'\\'+'Output'+'\\'+'Power_Offtake_Added'+'\\' + dates_folders[x]

                power_output_file = os.path.join(folder_path, temp_name + '.csv') 

                with open(vehicle_file_check, 'r') as f_in:

                    reader = csv.reader(f_in)
                    header = next(reader)
                    first_row = next(reader)
                    previous_lat = float(first_row[2])
                    previous_lon = float(first_row[3])
                    previous_time = float(first_row[1])
                    previous_speed = float(first_row[5])
                    previous_alt = float(first_row[4])


                    header_row = ("Minute of Day,Latitude,Longitude,Altitude,Speed,Displacement [m],Energy Used [kWh]")

                    with open(power_output_file, 'w') as f_out:

                        f_out.write(header_row + '\n')
                        line = "{},{},{},{},{},0,0".format(previous_time,previous_lat,previous_lon,previous_alt,previous_speed)+ "\n"
                        f_out.write(line)

                        for row in reader:
                            lat = float(row[2])
                            lon = float(row[3])
                            time = float(row[1])
                            speed = float(row[5])
                            alt = float(row[4])

                            previous_location = [previous_lat,previous_lon]
                            current_location = [lat,lon]
                            elev_change = alt-previous_alt
                            dist_lateral = geopy.distance.geodesic(previous_location,current_location).m
                            dist_traveled = np.sqrt(dist_lateral**2 + elev_change**2)

                            if dist_traveled != 0:
                                energy_discharge = (dist_traveled/1000)*(temp_efficiency) #kWh
                            else:
                                energy_discharge = 0

                            line = "{},{},{},{},{},{},{}".format(time,lat,lon,alt,speed,dist_traveled,energy_discharge)+ "\n"
                            f_out.write(line)

                            previous_lat = lat
                            previous_lon = lon
                            previous_time = time
                            previous_speed = speed
                            previous_alt = alt

def create_charging_stations_array(directory_path):
    global ChargingStations
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            with open(os.path.join(directory_path, filename), "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # Skip header row
                for row in csv_reader:
                    ChargingStations.append(row)
    

def charging_station_DF(Scenario_path):

    dir_charging_input = Scenario_path + '\\' + 'Input' + '\\' + 'Charging_Stations'
    charging_input_FILES = [f for f in os.listdir(dir_charging_input) if f.endswith('.csv')]

    create_charging_stations_array(dir_charging_input)

    global ChargingStationsDF
    global ChargingStationsObj
    global ChargingStations

    print('\nReading charging station inputs:')
    for i in tqdm(range(0,len(charging_input_FILES))):

        

        charging_station_file = os.path.join(dir_charging_input, charging_input_FILES[i])

        file_name, file_extension = os.path.splitext(charging_input_FILES[i])

        ChargingStationsDF[file_name] = pd.read_csv(charging_station_file)

        with open (charging_station_file, 'r') as f_in:

            reader = csv.reader(f_in)
            header = next(reader)

            file_name, file_extension = os.path.splitext(charging_input_FILES[i])

            for row in reader:
                temp_lat = (float)(row[0])
                temp_lon = (float)(row[1])
                temp_number_of_chargers = float(row[2])
                temp_speed = float(row[3])
                
                

                charging_station = ChargingStationClass(file_name,temp_lat,temp_lon,temp_number_of_chargers,temp_speed,temp_number_of_chargers,0,0,0)
                ChargingStationsObj.append(charging_station)

def create_dataframes_for_date(Scenario_path,current_date):

    #Directory of power offtake folders
    input_date = Scenario_path + '\\' + 'Output' + '\\' + 'Power_Offtake_Added' + '\\' + current_date
    mobility_FILES = [f for f in os.listdir(input_date) if f.endswith('.csv')]

    global todays_mobility_data

    for file in mobility_FILES:
        file_name, file_extension = os.path.splitext(file)
        file_path = Scenario_path + '\\' + 'Output' + '\\' + 'Power_Offtake_Added' + '\\' + current_date + '\\' + file
        todays_mobility_data[file_name] = pd.read_csv(file_path)

def get_charging_station_name(latitude, longitude):
    global ChargingStationsObj
    for charging_station in ChargingStationsObj:
        if charging_station.lat == float(latitude) and charging_station.lon == float(longitude):
            return charging_station.name

def decrease_battery_status(vehicle_name,energy_offtake):
    global Vehicles
    for vehicle in Vehicles:
        if vehicle.name == vehicle_name:
            vehicle.battery_status = float(vehicle.battery_status) - float(energy_offtake)
            if vehicle.battery_status < 0:
                vehicle.battery_status = 0
            break

def increase_battery_status(vehicle_name,energy_added):
    global Vehicles
    for vehicle in Vehicles:
        if vehicle.name == vehicle_name:

            temp_battery_status = float(vehicle.battery_status) + float(energy_added)

            if temp_battery_status > vehicle.battery_capacity:
                vehicle_charged = float(vehicle.battery_capacity) - float(vehicle.battery_status)
                vehicle.battery_status = vehicle.battery_capacity
                return vehicle_charged
            else:
                vehicle.battery_status = temp_battery_status
                return energy_added

def get_battery_status(name):
    global Vehicles
    for vehicle in Vehicles:
        if vehicle.name == name:
            return vehicle.battery_status

def is_charger_available(charging_station_name):
    for obj in ChargingStationsObj:
        if obj.name == charging_station_name:
            if obj.available_chargers > 0:
                return True
            else:
                return False
    return False

def get_charging_power(name):
    global ChargingStationsObj
    for station in ChargingStationsObj:
        if station.name == name:
            return station.charging_power
    return None

def is_battery_full(vehicle_name):
    global Vehicles
    for obj in Vehicles:
        if obj.name == vehicle_name:
            if obj.battery_status == obj.battery_capacity:
                return True
            else:
                return False
    return False

def set_where_charging(vehicle_name, charger_name):
    for vehicle in Vehicles:
        if vehicle.name == vehicle_name:
            vehicle.where_charging = charger_name

def check_charging_status(vehicle_name, charger_name):
    global Vehicles
    for vehicle in Vehicles:
        if vehicle.name == vehicle_name:
            if vehicle.where_charging == charger_name:
                return True
    return False

def reduce_available_chargers(charging_name):
    global ChargingStationsObj
    for station in ChargingStationsObj:
        if station.name == charging_name:
            station.available_chargers = int(station.available_chargers) - 1

def increase_available_chargers(charging_name):
    global ChargingStationsObj
    for station in ChargingStationsObj:
        if station.name == charging_name:
            station.available_chargers = int(station.available_chargers) + 1

def get_where_charging(vehicle_name):
    global Vehicles
    for vehicle in Vehicles:
        if vehicle.name == vehicle_name:
            return vehicle.where_charging
    return None

def battery_flat(vehicle_name, current_lat, current_lon, current_date, minute_of_day):
    global Vehicles
    global Batterty_Flat
    
    for vehicle in Vehicles:
        if vehicle.name == vehicle_name and vehicle.battery_status <= 0:
            Batterty_Flat = True

            hour = str(int(float(minute_of_day)/60))
            if len(hour) == 1:
                hour = '0' + hour[0]
            minute = str(int(float(minute_of_day) % 60))
            if len(minute) == 1:
                minute = '0' + minute[0]
            print("\nThe simulation could not be completed. It was stopped on {} at {}:{}:00 as Vehicle {}'s battery reached 0 at ({},{}). Either increase battery size, or ensure charging prior to this timestamp.".format(current_date, hour,minute, vehicle_name, current_lat, current_lon))
            
def is_it_charging(Scenario_path,current_date):

    
    path = Scenario_path+'\\'+'Output'+'\\'+'Battery_Level_Added'
    os.chdir(path)
    os.makedirs(current_date) 

    


    output_dir = Scenario_path+'\\'+'Output'+'\\'+'Battery_Level_Added'+'\\'+current_date

    header_row = "Minute of Day,Latitude,Longitude,Altitude,Speed,Displacement [m],Energy Used [kWh],Battery Charged [kWh],Battery Level [kWh],Where I'm Charging"

    #Directory of power offtake folders
    input_date = Scenario_path + '\\' + 'Output' + '\\' + 'Power_Offtake_Added' + '\\' + current_date
    mobility_FILES = [os.path.join(input_date, file) for file in os.listdir(input_date) if file.endswith('.csv')]


    for input_file in mobility_FILES:
        # Get the file name without the path and extension
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_dir, file_name + ".csv")
        # Create the output file and write the header row
        with open(output_file, "w") as f:
            f.write(header_row + "\n")
            
    readers = [csv.reader(open(file, 'r')) for file in mobility_FILES]

    global ChargingStations
    global Batterty_Flat

    for reader in readers:
        next(reader) # Skip the header row in each file

    for rows in zip(*readers):

        if Batterty_Flat:
            break

        for i, row in enumerate(rows):

            current_minute = row[0]
            current_lat = float(row[1])
            current_lon = float(row[2])
            current_alt = row[3]
            current_speed = float(row[4])
            displacement = float(row[5])
            energy_offtake = float(row[6])
            
            vehicle = os.path.splitext(os.path.basename(mobility_FILES[i]))[0]

            charging_found = False

            

            write = False

                

            #ADD CHECK TO SEE IF BATTERY IS FULL
            is_battery_fulll = is_battery_full(vehicle)

            if is_battery_fulll == False:  #Battery is not full and recharging can by explored

                if current_speed == 0.0:

                    for i in range(len(ChargingStations)):

                        upper_lat = float(ChargingStations[i][0]) + 0.0000450665*charging_radius
                        lower_lat = float(ChargingStations[i][0]) - 0.0000450665*charging_radius
                        upper_lon = float(ChargingStations[i][1]) + 0.0000569195*charging_radius
                        lower_lon = float(ChargingStations[i][1]) - 0.0000569195*charging_radius

                        

                        if (current_lat<float(upper_lat) and current_lat>float(lower_lat)) and (current_lon<float(upper_lon) and current_lon>float(lower_lon)):
                            charging_found = True
                            #Vehicle is close to charging station and has 0 speed
                            #The name of which charging station it is close to is now returned
                            charging_station_name = get_charging_station_name(ChargingStations[i][0], ChargingStations[i][1])
                            
                            

                            #This function will check if a charger is avialable at the current charging station
                            available_charger = is_charger_available(charging_station_name)

                            #Check to see if the vehicle is still at the same charging station
                            same_charging_point = check_charging_status(vehicle, charging_station_name)
                            
                            
                            if same_charging_point == True:   #Vehicle is already charging at this station
                                #!!!!!!!!!!CHARGING!!!!!!!!!!

                                output_file_temp = os.path.join(output_dir, vehicle + ".csv")
                                charging_power = get_charging_power(charging_station_name) #kW
                                temp_vehicle_charged = float(charging_power)/60       #kWh charged in this minute
                                decrease_battery_status(vehicle,energy_offtake)
                                battery_flat(vehicle, current_lat, current_lon, current_date, current_minute)
                                vehicle_charged = increase_battery_status(vehicle,temp_vehicle_charged)
                                new_battery_status = float(get_battery_status(vehicle))
                                where_charging = get_where_charging(vehicle)

                                with open(output_file_temp, 'a') as f_out:
                                    line = "{},{},{},{},{},{},{},{},{},{}".format(current_minute,current_lat,current_lon,current_alt,current_speed,displacement,energy_offtake,vehicle_charged,new_battery_status,where_charging) + "\n"
                                    f_out.write(line)
                                    write = True
                            
                            
                            elif available_charger == True and write == False :   #Vehicle is new to this station, reduce the number of chargers available and set name of station
                                #!!!!!!!!!!CHARGING!!!!!!!!!!

                                #Sets the name of where it is currently charging
                                set_where_charging(vehicle, charging_station_name)
                                where_charging = get_where_charging(vehicle)

                                #Reduce the number of chargers avialable
                                reduce_available_chargers(charging_station_name)

                                output_file_temp = os.path.join(output_dir, vehicle + ".csv")
                                charging_power = get_charging_power(charging_station_name) #kW
                                temp_vehicle_charged = float(charging_power)/60       #kWh charged in this minute
                                decrease_battery_status(vehicle,energy_offtake)
                                battery_flat(vehicle, current_lat, current_lon, current_date, current_minute)
                                vehicle_charged = increase_battery_status(vehicle,temp_vehicle_charged)
                                new_battery_status = float(get_battery_status(vehicle))

                                with open(output_file_temp, 'a') as f_out:
                                    line = "{},{},{},{},{},{},{},{},{},{}".format(current_minute,current_lat,current_lon,current_alt,current_speed,displacement,energy_offtake,vehicle_charged,new_battery_status,where_charging) + "\n"
                                    f_out.write(line)
                                    write = True

                            break
                        



                    if charging_found == False and write == False:    
                        #Vehicle is not close to a charging station so it can be concluded vehicle is definietly not charging. Add current battery level to dataframe and print
                        decrease_battery_status(vehicle,energy_offtake)
                        battery_flat(vehicle, current_lat, current_lon, current_date, current_minute)
                        output_file_temp = os.path.join(output_dir, vehicle + ".csv")
                        current_battery_status = get_battery_status(vehicle)

                        with open(output_file_temp, 'a') as f_out:
                            line = "{},{},{},{},{},{},{},0,{},".format(current_minute,current_lat,current_lon,current_alt,current_speed,displacement,energy_offtake,current_battery_status) + "\n"
                            f_out.write(line)
                            write =  True

                        where_charging = get_where_charging(vehicle)
                        if where_charging != 'N/A':   #Vehicle was charging in the previous datapoint
                            set_where_charging(vehicle, 'N/A')
                            increase_available_chargers(where_charging)


                        
                        

                    elif available_charger == False and write == False:
                        #Vehicle is close to a charging station, but no charger is available so it can be concluded vehicle is definietly not charging. Add current battery level to dataframe and print
                        decrease_battery_status(vehicle,energy_offtake)
                        battery_flat(vehicle, current_lat, current_lon, current_date, current_minute)
                        output_file_temp = os.path.join(output_dir, vehicle + ".csv")
                        current_battery_status = get_battery_status(vehicle)

                        with open(output_file_temp, 'a') as f_out:
                            line = "{},{},{},{},{},{},{},0,{},".format(current_minute,current_lat,current_lon,current_alt,current_speed,displacement,energy_offtake,current_battery_status) + "\n"
                            f_out.write(line)
                            write = True

                        where_charging = get_where_charging(vehicle)
                        if where_charging != 'N/A':   #Vehicle was charging in the previous datapoint
                            set_where_charging(vehicle, 'N/A')
                            increase_available_chargers(where_charging)

                else:
                    #Vehicle is on the move so it can be concluded vehicle is definietly not charging. Add current battery level to dataframe and print
                    decrease_battery_status(vehicle,energy_offtake)
                    battery_flat(vehicle, current_lat, current_lon, current_date, current_minute)
                    output_file_temp = os.path.join(output_dir, vehicle + ".csv")
                    current_battery_status = get_battery_status(vehicle)

                    with open(output_file_temp, 'a') as f_out:
                        line = "{},{},{},{},{},{},{},0,{},".format(current_minute,current_lat,current_lon,current_alt,current_speed,displacement,energy_offtake,current_battery_status) + "\n"
                        f_out.write(line)
                        write = True

                    where_charging = get_where_charging(vehicle)
                    if where_charging != 'N/A':   #Vehicle was charging in the previous datapoint
                        set_where_charging(vehicle, 'N/A')
                        increase_available_chargers(where_charging)

            else:  #Battery is full and charging cannot take place
                decrease_battery_status(vehicle,energy_offtake)
                battery_flat(vehicle, current_lat, current_lon, current_date, current_minute)
                output_file_temp = os.path.join(output_dir, vehicle + ".csv")
                current_battery_status = get_battery_status(vehicle)

                with open(output_file_temp, 'a') as f_out:
                    line = "{},{},{},{},{},{},{},0,{},".format(current_minute,current_lat,current_lon,current_alt,current_speed,displacement,energy_offtake,current_battery_status) + "\n"
                    f_out.write(line)
                    write = True

                where_charging = get_where_charging(vehicle)
                if where_charging != 'N/A':   #Vehicle was charging in the previous datapoint
                    set_where_charging(vehicle, 'N/A')
                    increase_available_chargers(where_charging)

def add_charger_active(name):
    global ChargingStationsObj
    for obj in ChargingStationsObj:
        if obj.name == name:
            obj.chargers_active += 1
            break

def add_energy_delivered(charging_station_name, energy_to_add):
    global ChargingStationsObj
    for station in ChargingStationsObj:
        if station.name == charging_station_name:
            station.energy_delivered += energy_to_add
            break

def add_daily_energy_delivered(charging_station_name, energy_to_add):
    global ChargingStationsObj
    for station in ChargingStationsObj:
        if station.name == charging_station_name:
            current_daily_energy = station.daily_energy_delivered
            next_daily_energy = current_daily_energy + energy_to_add
            temp = round(next_daily_energy, 6)
            station.daily_energy_delivered = round(next_daily_energy, 6)
            break

def get_chargers_active(charging_station_name):
    global ChargingStationsObj
    for station in ChargingStationsObj:
        if station.name == charging_station_name:
            return station.chargers_active

def get_charging_power(charging_station_name):
    global ChargingStationsObj
    for obj in ChargingStationsObj:
        if obj.name == charging_station_name:
            return obj.charging_power

def get_energy_delivered(charging_station_name):
    global ChargingStationsObj
    for station in ChargingStationsObj:
        if station.name == charging_station_name:
            return station.energy_delivered

def get_daily_energy_delivered(charging_station_name):
    global ChargingStationsObj
    for station in ChargingStationsObj:
        if station.name == charging_station_name:
            return station.daily_energy_delivered

def reset_chargers_active(charging_station_name):
    global ChargingStationsObj
    for obj in ChargingStationsObj:
        if obj.name == charging_station_name:
            obj.chargers_active = 0

def reset_energy(charging_station_name):
    global ChargingStationsObj
    for obj in ChargingStationsObj:
        if obj.name == charging_station_name:
            obj.energy_delivered = 0

def reset_daily_energy(charging_station_name):
    global ChargingStationsObj
    for obj in ChargingStationsObj:
        if obj.name == charging_station_name:
            obj.daily_energy_delivered = 0

def grid_impact(Scenario_path,current_date):

    path = Scenario_path+'\\'+'Output'+'\\'+'Charging_Stations'
    os.chdir(path)
    os.makedirs(current_date) 

    charging_output_dir = Scenario_path+'\\'+'Output'+'\\'+'Charging_Stations'+'\\' + current_date
    #Create output files for charging stations
    header_row = "Time [min],Chargers Active,Power Delivery [kW],Energy Delivery [kWh],Cumulative Daily Energy [kWh]"
    global ChargingStationsObj
    for station in ChargingStationsObj: 
        output_file = os.path.join(charging_output_dir, station.name + ".csv")
        with open(output_file, 'w') as f:
            f.write(header_row + "\n")


    #Directory of power offtake folders
    input_date = Scenario_path + '\\' + 'Output' + '\\' + 'Battery_Level_Added' + '\\' + current_date
    charged_FILES = [os.path.join(input_date, file) for file in os.listdir(input_date) if file.endswith('.csv')]

    readers = [csv.reader(open(file, 'r')) for file in charged_FILES]

    #Clear the daily energy delivered in CharginStationObj
    for station in ChargingStationsObj: 
        reset_daily_energy(station.name)


    for reader in readers:
        next(reader) # Skip the header row in each file

    for rows in zip(*readers):
        for i, row in enumerate(rows):

            currenct_charger = row[9]
            minute = row[0]

            if currenct_charger != '':   #Vehicle is charging

                add_charger_active(currenct_charger)

                energy_delivered = float(row[6])
                add_energy_delivered(currenct_charger, energy_delivered)
                add_daily_energy_delivered(currenct_charger, energy_delivered)

        #Print all chargin station information
        for station in ChargingStationsObj: 
            output_file = os.path.join(charging_output_dir, station.name + ".csv")
            chargers_active = get_chargers_active(station.name)
            power = chargers_active * (get_charging_power(station.name))
            energy_delivered_now = get_energy_delivered(station.name)
            energy_delivered_daily = float(get_daily_energy_delivered(station.name))
            with open(output_file, 'a') as f:
                line = "{},{},{},{},{}".format(minute,chargers_active,power,energy_delivered_now,energy_delivered_daily)
                f.write(line + "\n")

            #Clear the current energy delivered and active chargers in CharginStationObj
            reset_chargers_active(station.name)
            reset_energy(station.name)

def load_profiles(charging_output_dir):
    # Loop through each day's directory
    print('\nGenerating charging station load profiles:')
    for day_dir in tqdm(os.listdir(charging_output_dir)):
        day_path = os.path.join(charging_output_dir, day_dir)
        
        # Loop through each charging station's CSV file
        for csv_file in os.listdir(day_path):
            if not csv_file.endswith('.csv'):
                continue

            csv_path = os.path.join(day_path, csv_file)
            
            # Load CSV data into a pandas dataframe
            df = pd.read_csv(csv_path)
            
            # Plot the power delivered vs time
            plt.plot(df['Time [min]'], df['Power Delivery [kW]'], linewidth=1)
            plt.xlabel('Time [min]')
            plt.ylabel('Power Delivery [kW]')
            plt.ylim(0, 100)
            plt.title(csv_file[:-4])
            
            # Save the plot as PNG file
            plot_path = os.path.join(day_path, csv_file[:-4]+"_Power_Profile" + '.png')
            plt.savefig(plot_path)
            
            # Clear the plot for next iteration
            plt.clf()

def energy_profiles(charging_output_dir):
    # Loop through each day's directory
    print('\nGenerating charging station energy profiles:')
    for day_dir in tqdm(os.listdir(charging_output_dir)):
        day_path = os.path.join(charging_output_dir, day_dir)
        
        # Loop through each charging station's CSV file
        for csv_file in os.listdir(day_path):
            if not csv_file.endswith('.csv'):
                continue

            csv_path = os.path.join(day_path, csv_file)
            
            # Load CSV data into a pandas dataframe
            df = pd.read_csv(csv_path)
            
            # Plot the power delivered vs time
            plt.plot(df['Time [min]'], df['Cumulative Daily Energy [kWh]'])
            plt.xlabel('Time [min]')
            plt.ylabel('Cumulative Daily Energy [kWh]')
            plt.ylim(0, 300)
            plt.title(csv_file[:-4])
            
            # Save the plot as PNG file
            plot_path = os.path.join(day_path, csv_file[:-4]+"_Energy_Profile" + '.png')
            plt.savefig(plot_path)
            
            # Clear the plot for next iteration
            plt.clf()

def plot_average_power_vs_time(charging_output_dir):
    # Get the list of all day directories
    day_dirs = [day_dir for day_dir in os.listdir(charging_output_dir) if os.path.isdir(os.path.join(charging_output_dir, day_dir))]
    
    # Create a dictionary to store the cumulative power for each charging station
    charging_stations = {}
    
    # Loop through each day directory
    for day_dir in day_dirs:
        day_path = os.path.join(charging_output_dir, day_dir)
        
        # Loop through each charging station's CSV file
        for csv_file in os.listdir(day_path):
            # Check if the file is a CSV file
            if not csv_file.endswith('.csv'):
                continue
            
            csv_path = os.path.join(day_path, csv_file)
            
            # Load CSV data into a pandas dataframe
            df = pd.read_csv(csv_path)
            
            # Get the power column from the dataframe
            power = df['Power Delivery [kW]'].values
            
            # Pad the array with NaNs if it's length is less than 1440 (24 hours x 60 minutes)
            if len(power) < 1440:
                power = np.pad(power, (0, 1440-len(power)), 'constant', constant_values=(np.nan, np.nan))
            
            # Add the power values to the cumulative power dictionary
            if csv_file in charging_stations:
                charging_stations[csv_file] = np.vstack((charging_stations[csv_file], power))
            else:
                charging_stations[csv_file] = np.array([power])
    
    # Plot the average power versus time for each charging station
    print('\nGenerating average power delivery for all charging stations:')
    for charging_station, power_values in tqdm(charging_stations.items()):
        # Calculate the average power for each minute of the day
        average_power = np.nanmean(power_values, axis=0)
        
        # Plot the average power versus time
        plt.plot(average_power, label=charging_station[:-4])
        
    plt.xlabel('Time [min]')
    plt.ylabel('Power [kW]')
    plt.title("Average Power versus Time for All Charging Stations")
    plt.legend()
    
    # Save the plot as PNG file
    plot_path = os.path.join(charging_output_dir, "Average_Power_versus_Time" + '.png')
    plt.savefig(plot_path)
    
    # Clear the plot for next iteration
    plt.clf()

def plot_average_energy_vs_time(charging_output_dir):
    # Get the list of all day directories
    day_dirs = [day_dir for day_dir in os.listdir(charging_output_dir) if os.path.isdir(os.path.join(charging_output_dir, day_dir))]
    
    # Create a dictionary to store the cumulative power for each charging station
    charging_stations = {}
    
    # Loop through each day directory
    for day_dir in day_dirs:
        day_path = os.path.join(charging_output_dir, day_dir)
        
        # Loop through each charging station's CSV file
        for csv_file in os.listdir(day_path):
            # Check if the file is a CSV file
            if not csv_file.endswith('.csv'):
                continue
            
            csv_path = os.path.join(day_path, csv_file)
            
            # Load CSV data into a pandas dataframe
            df = pd.read_csv(csv_path)
            
            # Get the power column from the dataframe
            power = df['Cumulative Daily Energy [kWh]'].values
            
            # Pad the array with NaNs if it's length is less than 1440 (24 hours x 60 minutes)
            if len(power) < 1440:
                power = np.pad(power, (0, 1440-len(power)), 'constant', constant_values=(np.nan, np.nan))
            
            # Add the power values to the cumulative power dictionary
            if csv_file in charging_stations:
                charging_stations[csv_file] = np.vstack((charging_stations[csv_file], power))
            else:
                charging_stations[csv_file] = np.array([power])
    
    # Plot the average power versus time for each charging station
    print('\nGenerating average cumulative daily energy for all charging stations:')
    for charging_station, power_values in tqdm(charging_stations.items()):
        # Calculate the average power for each minute of the day
        average_power = np.nanmean(power_values, axis=0)
        
        # Plot the average power versus time
        plt.plot(average_power, label=charging_station[:-4])
        
    plt.xlabel('Time [min]')
    plt.ylabel('Cumulative Daily Energy [kWh]')
    plt.title("Average Energy versus Time for All Charging Stations")
    plt.legend()
    
    # Save the plot as PNG file
    plot_path = os.path.join(charging_output_dir, "Average_Energy_versus_Time" + '.png')
    plt.savefig(plot_path)
    
    # Clear the plot for next iteration
    plt.clf()

def run(Scenario_path):

    #offtake_power(Scenario_path)
    folder_path = Scenario_path + '\\' + 'Output' + '\\' + '24h_Extrapolated_Data'
    #if delete_folders == True:
    #    shutil.rmtree(folder_path)

    

    #Craete objects for all the charging stations
    charging_station_DF(Scenario_path)

    
    dir_power_offtake = Scenario_path + '\\' + 'Output' + '\\' + 'Power_Offtake_Added'
    dates_list = [f for f in os.listdir(dir_power_offtake) if os.path.isdir(os.path.join(dir_power_offtake, f))]

    path = Scenario_path+'\\'+'Output'
    os.chdir(path)
    #os.makedirs('Battery_Level_Added') 

    path = Scenario_path+'\\'+'Output'
    os.chdir(path)
    os.makedirs('Charging_Stations') 

    
    

    global todays_mobility_data
    global Batterty_Flat


    print('\nGrid-Sim Running')
    for i in tqdm(range(0,len(dates_list))):

        if Batterty_Flat:
            break

        #For this date, create a dataframe with all mobility data
        create_dataframes_for_date(Scenario_path,dates_list[i])

        #With the dataframes created, go through it row by row and do charging
        #is_it_charging(Scenario_path,dates_list[i])
        grid_impact(Scenario_path,dates_list[i])



    charging_station_ouput = Scenario_path+'\\'+'Output'+'\\'+'Charging_Stations'
    load_profiles(charging_station_ouput)
    energy_profiles(charging_station_ouput)

    plot_average_power_vs_time(charging_station_ouput)
    plot_average_energy_vs_time(charging_station_ouput)

    







def main(scenario_dir: Path):

    #User to input scenaio path
    Scenario_path = input('\nWelcome to Grid-Sim. Please enter the path for this scenario: ')
    while not (os.path.exists(Scenario_path)):
        print('\nFolder path does not exist\n')
        Scenario_path = input('Please enter the path for this scenario: ')


    #Selection menue
    selection = input('\nPlease select an option:\n0. Initialise Scenario\n1. Check and Prepare Files\n2. Run Grid-Sim\n') 
    while not (selection=='0' or selection=='1' or selection=='2'):
        selection = input('\nInvalid option. Please enter a valid option: ')
    
    
    if selection == '0':
        initialise(Scenario_path)

    if selection=='1' or initialise_done==True:
        check_and_prepare(Scenario_path)

    if selection=='2' or prep_done==True:
        run(Scenario_path)



if __name__ == '__main__':
    scenario_dir = Path(os.path.abspath(__file__)).parents[2]  # XXX This isn't working when pdb is loaded...
    main(scenario_dir)


    