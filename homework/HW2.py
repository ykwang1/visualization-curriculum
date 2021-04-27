import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

def get_cali_data(path_to_csv):
    raw_data = pd.read_csv('AIS_2020_06_11.csv')

    raw_data.dropna(subset=['VesselType', 'Status'], inplace=True)

    lat_min = 32.56
    lat_max = 42
    lon_min = -126
    lon_max = -117

    vessel_type_dict = {0: np.nan, 30: 'Fishing', 31: 'Tug', 32: 'Tug', 33: 'Dredger', 34:'Dive Vessel', 35: 'Military Ops',
                       36: 'Sailing Vessel', 37: 'Pleasure Craft', 38: np.nan, 40: 'High-Speed Craft', 47: 'High-Speed Craft',
                       60: 'Passenger', 70:'Cargo', 79:'Cargo', 80:'Tanker', 89:'Tanker'}

    status_dict = {0: 'Under way using engine', 1: 'At anchor', 3:'Restricted manoeuverability', 5:'Moored', 7:'Fishing', 
                  8: 'Under way sailing'}

    cali_data = raw_data.query(f'({lat_max} > LAT > {lat_min}) & ({lon_max} > LON > {lon_min})')

    MMSIs = cali_data['MMSI'].value_counts()[cali_data['MMSI'].value_counts() > 100].index
    cali_data = cali_data[cali_data['MMSI'].isin(MMSIs)]
    cali_data['BaseDateTime'] = pd.to_datetime(cali_data['BaseDateTime'])

    cali_data['VesselType'] = [vessel_type_dict[ii] if ii in vessel_type_dict else np.nan for ii in cali_data['VesselType']]
    cali_data['Status'] = [status_dict[ii] if ii in status_dict else np.nan for ii in cali_data['Status']]
    cali_data.dropna(subset=['VesselType', 'Status'], inplace=True)
    
    return cali_data

def get_data_subset(data, lat_min, lat_max, lon_min, lon_max):
    return data.query(f'({lat_max} > LAT > {lat_min}) & ({lon_max} > LON > {lon_min})')

def get_bay_data(cali_data):
    bay_lat_min = 37.55229
    bay_lat_max = 38.10289
    bay_lon_min = -123
    bay_lon_max = -122.12904

    bay_data = get_data_subset(cali_data, bay_lat_min, bay_lat_max, bay_lon_min, bay_lon_max)
    bay_data = bay_data.sort_values(['MMSI', 'BaseDateTime'] )
    bay_data['Region'] = 'Bay Area'
    return bay_data
    
def get_la_data(cali_data):
    la_lat_min = 33.374264
    la_lat_max = 34.
    la_lon_min = -119.18628
    la_lon_max = -117.59925
    la_data = get_data_subset(cali_data, la_lat_min, la_lat_max, la_lon_min, la_lon_max)
    la_data = la_data.sort_values(['MMSI', 'BaseDateTime'] )
    la_data['Region'] = 'LA'
    return la_data

def plot_ship_tracks(data):
    fig, ax = plt.subplots(figsize=(15,10))
    for MMSI in data['MMSI'].unique():
        data.query(f'MMSI == {MMSI}').plot(x='LON', y='LAT', color='k', stacked=True, ax=ax, legend=False, alpha=.15)
        
def plot_by_hour(data1, data2, label1, label2, bins):
    plt.style.use('ggplot')
    plt.rc('font', size=16)
    fig, axs = plt.subplots(5, 1, sharey=True, sharex=True, figsize=(15,12))
    fig.tight_layout()
    for ii, vtype in enumerate(data1['VesselType'].unique()):
        axs[ii].set_title(vtype, y = .75, weight='bold', fontsize=14)
        axs[ii].hist(data1.query(f"VesselType == '{vtype}'")['timeByMinute'], bins=bins , alpha=.5, label=label1)
        axs[ii].hist(data2.query(f"VesselType == '{vtype}'")['timeByMinute'], bins=bins, alpha=.5, label=label2)
    handles, labels = axs[ii].get_legend_handles_labels()
    plt.legend( handles, labels, loc = 'lower center', bbox_to_anchor = (0, -.06,1,1),
                bbox_transform = plt.gcf().transFigure, ncol=3)

    plt.xlim(xmin=bins.min(), xmax=bins.max())
    plt.suptitle("AIS Transmissions per Hour", fontsize=20, y=1.01)
    plt.xlim(xmin=bins.min(), xmax=bins.max())
    axs[2].set_ylabel("Transmissions/Hour")
    plt.xlabel("Local Time (06/10/20 - 06/11/20)")
    axs[ii].xaxis.set_major_locator(mdates.MinuteLocator(interval=120))   #to get a tick every 15 minutes
    axs[ii].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))   
    # plt.show()