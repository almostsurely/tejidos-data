
from os import getenv
import urllib.request 
import json 
import pandas as pd

def json_from_url(url_):
	with urllib.request.urlopen(url_) as url:
		jsonurl = json.loads(url.read().decode())
	return(jsonurl)

def get_access_token(client_id, client_secret):
	gat_url = 'https://pubsbapi-latam.smartbike.com/oauth/v2/token?client_id='+client_id+\
	              '&client_secret='+client_secret+'&grant_type=client_credentials'
	access_data = json_from_url(gat_url)
	return(access_data['access_token'])

def get_station_list(access_token):
	gsl_url = 'https://pubsbapi-latam.smartbike.com/api/v1/stations.json?access_token='+access_token
	station_list = json_from_url(gsl_url)
	station_df = pd.DataFrame.from_dict(station_list['stations'])
	return(station_df)

def get_station_disponibility(access_token):
	gsd_url = 'https://pubsbapi-latam.smartbike.com/api/v1/stations/status.json?access_token='+access_token
	station_disp = json_from_url(gsd_url)
	station_df = pd.DataFrame.from_dict(station_disp['stationsStatus'])
	return(station_df)

def main():
	### 
	client_id = getenv('my_ecobici_client_id')
	client_secret = getenv('my_ecobici_client_secret')
	###

	token = get_access_token(client_id, client_secret)

	station_list = get_station_list(token)

	#station_list.to_csv('data_ecobici/station_list.csv', sep=',', encoding='utf-8')

	get_station_disponibility = get_station_disponibility(token)

	#station_disponibility.to_csv('data_ecobici/station_disponibility.csv', sep=',', encoding='utf-8')

if __name__ == "__main__":
	main()

