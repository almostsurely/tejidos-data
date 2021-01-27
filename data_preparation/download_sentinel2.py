
from sentinelsat import SentinelAPI
from sentinelsat import read_geojson
from sentinelsat import geojson_to_wkt
from datetime import date
from os import path
from os import getenv
from zipfile import ZipFile


def current_month():
	dat = date.today().strftime('%Y%m')
	return(dat)

def api_connect(user, pasw, scihuburl = 'https://scihub.copernicus.eu/dhus'):
	api = SentinelAPI(user, pasw, scihuburl)
	return(api)

def api_query(api, footprint, date, platformname = 'Sentinel-2', cloudcoverpercentage = (0,100)):
	query = api.query(area = footprint,
					  date = date,
					  platformname = platformname,
					  cloudcoverpercentage = cloudcoverpercentage)

	query = api.to_dataframe(query)
	return(query)

# Obtains most current product from a scihub query-dataframe. 
def last_product(df):
	df_sorted = df.sort_values(['ingestiondate'], ascending=[False])
	df_sorted = df_sorted.head(1)
	return(df_sorted)

# Checks if compressed product exists. 
# If not, downloads it. 
# Returns name of file.
def download_product(api, product):
	product_name = str(product['title'][0]) + '.zip'
	if not path.exists(product_name):
		api.download_all(product.index)
	return(product_name)

def main():
	### 
	scihub_user = getenv('my_scihub_user')
	scihub_pasw = getenv('my_scihub_pasw')
	footprint_path = 'data_polygons/roi_extent.geojson'
	###

	api = api_connect(scihub_user, scihub_pasw)

	footprint = geojson_to_wkt(read_geojson(footprint_path))

	products = api_query(api , footprint, (current_month() + '01',current_month() + '31'))

	product = last_product(products)

	product_name = download_product(api, product)

	zipfile = ZipFile(product_name, 'r')

	zipfile.extractall(r'data_sentinel')

	zipfile.close()

if __name__ == "__main__":
	main()