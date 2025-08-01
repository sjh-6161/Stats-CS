import boto3
from botocore import UNSIGNED
from botocore.client import Config

# s12/Combines/08-19/combine-challenger-mid1385-1_de_nuke-2023-08-20_03-22-48.dem.zip
prefixes = [
    's17/Combines/04-26', 
    's17/Combines/04-28', 
    's17/Combines/04-29', 
    's17/Combines/05-01', 
    's17/Combines/05-03', 
    's17/Combines/05-05', 
    's17/Combines/05-06', 
    's17/Combines/05-08', 
    's17/Combines/05-10'
]

for prefix in prefixes:
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='nyc3',
                            endpoint_url='https://nyc3.digitaloceanspaces.com',
                            config=Config(signature_version=UNSIGNED))

    response = client.list_objects(Bucket='cscdemos', Prefix=prefix)

    keys = [item['Key'] for item in response['Contents']]


    for key in keys:
        filename = "demos_download/" + '-'.join(key.split('/')[-2:])
        print('now doing',filename)
        with open(filename, 'wb') as f:
            client.download_fileobj('cscdemos', key, f)