import re
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from botocore.exceptions import ClientError
import zipfile
import os

def get_mid(filename):
    match = re.search(r'mid\d+', filename)
    return match.group() if match else None

# s12/Combines/08-19/combine-challenger-mid1385-1_de_nuke-2023-08-20_03-22-48.dem.zip
prefixes = [
    's19/M01',
    's19/M02',
    's19/M03',
    's19/M04',
    's19/M05',
    's19/M06',
    's19/M07',
    's19/M08',
    's19/M09',
    's19/M10',
]

for prefix in prefixes:
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            config=Config(signature_version=UNSIGNED))

    response = client.list_objects(Bucket='cscdemos', Prefix=prefix)

    keys = [item['Key'] for item in response['Contents']]

    existing_dems = os.listdir("D:\CSC\Season 19")

    existing_mids = {get_mid(f) for f in existing_dems}

    for index, key in enumerate(keys):
        try:
            print(str(index) + "/" + str(len(keys)))

            if "Scrim" in key: continue
            if get_mid(key) in existing_mids:
                continue

            filename = "D:/CSC/Season 19/" + '-'.join(key.split('/')[-2:])
            print('now doing',filename)

            with open(filename, 'wb') as f:
                client.download_fileobj('cscdemos', key, f)


            with zipfile.ZipFile(filename, 'r') as zf:
                zf.extractall("D:/CSC/Season 19/")

            print(f"Successfully unzipped '{filename}' to D:/CSC/Season 19/")

            os.remove(filename)
        except ClientError as e:
            print(e)