from math import cos, asin, sqrt, pi
import pandas as pd
from geopy import distance


def closest(data, v):
    """ Set closest distance and POIID for a record based on

    :param data:
    :param v:
    :return:
    """
    min_dist = float('inf')
    location = None
    for _, row in v.iterrows():
        # dist = distance(data['Latitude'], data['Longitude'], row['Latitude'], row['Longitude'])
        dist = distance.distance((data['Latitude'], data['Longitude']), (row['Latitude'], row['Longitude'])).km
        if dist < min_dist:
            location = row['POIID']
            min_dist = dist

    return [min_dist, location]


def get_clean_df(path, keys=None):
    df = pd.read_csv(path, skipinitialspace=True)
    # df.columns = [x.strip() for x in df.columns]
    if keys is not None:
        df = df.drop_duplicates(keys)
    return df


def main(data_file, poi_list_file, output_file):
    """
    1. Cleanup
    A sample dataset of request logs is given in data/DataSample.csv. We consider records that have identical geoinfo and timest as suspicious. Please clean up the sample dataset by filtering out those suspicious request records.
    """
    # _ID, TimeSt,Country,Province,City,Latitude,Longitude
    df = get_clean_df(data_file, ['TimeSt', 'Latitude', 'Longitude'])

    """
    2. Label
    Assign each request (from data/DataSample.csv) to the closest (i.e. minimum distance) POI (from data/POIList.csv).
    
    Note: a POI is a geographical Point of Interest.
    """
    poi_df = get_clean_df(poi_list_file, ['Latitude', 'Longitude'])

    df['label'] = df[['Latitude', 'Longitude']].apply(closest, axis=1, args=[poi_df])

    df[['distance', 'POIID']] = pd.DataFrame(df['label'].values.tolist(), index=df.index)

    """
    3. Analysis
    For each POI, calculate the average and standard deviation of the distance between the POI to each of its assigned requests.
    At each POI, draw a circle (with the center at the POI) that includes all of its assigned requests. Calculate the radius and density (requests/area) for each POI.
    """
    df = df.groupby(['POIID'], as_index=False).agg({'distance': ['mean', 'std', 'count', 'max']})

    df['mean (Kms)'] = df['distance']['mean']
    df['std'] = df['distance']['std']
    df['radius (Kms)'] = df['distance']['max']
    df['density (/Km)'] = df['distance']['count'] / (2 * pi * df['radius (Kms)'])

    del df['distance']

    df.to_csv(output_file)


if __name__ == "__main__":
    main("DataSample.csv", "POIList.csv", "output.csv")



