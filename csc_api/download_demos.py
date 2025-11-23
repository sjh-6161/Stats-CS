import boto3
from botocore import UNSIGNED
from botocore.client import Config
import zipfile
import os

# s12/Combines/08-19/combine-challenger-mid1385-1_de_nuke-2023-08-20_03-22-48.dem.zip
prefixes = [
    's18/M01',
    's18/M02',
    's18/M03',
    's18/M04',
    's18/M05',
    's18/M06',
    's18/M07',
    's18/M08',
    's18/M09',
    's18/M10',
    's18/M11',
    's18/M12',
    's18/M13',
]

for prefix in prefixes:
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            config=Config(signature_version=UNSIGNED))

    response = client.list_objects(Bucket='cscdemos', Prefix=prefix)

    keys = [item['Key'] for item in response['Contents']]

    existing_dems = os.listdir("D:\CSC\Season 18")

    for key in keys:
        if "Scrim" in key: continue
        if key[8:-4] in existing_dems: 
            continue

        filename = "D:/CSC/Season 18/" + '-'.join(key.split('/')[-2:])
        print('now doing',filename)

        with open(filename, 'wb') as f:
            client.download_fileobj('cscdemos', key, f)


        with zipfile.ZipFile(filename, 'r') as zf:
            zf.extractall("D:/CSC/Season 18/")

        print(f"Successfully unzipped '{filename}' to D:/CSC/Season 18/")

        os.remove(filename)