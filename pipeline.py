import re
import os
import shutil
import tempfile
import zipfile
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from botocore.exceptions import ClientError
from tqdm import tqdm
from data import DbConnection, FailedDemo
from parse import parse_one_demo, parser_version


def get_s3_client():
    session = boto3.session.Session()
    return session.client(
        's3',
        region_name='nyc3',
        endpoint_url='https://nyc3.digitaloceanspaces.com',
        config=Config(signature_version=UNSIGNED),
    )


def extract_mid(s3_key: str):
    match = re.search(r'mid\d+', s3_key)
    return match.group() if match else None


def get_stage(stage_type: str, s3_key: str) -> str:
    """Determine the stage string to store in the match table."""
    if stage_type == "regulation":
        return "Regulation"
    elif stage_type == "preseason":
        return "Preseason"
    elif stage_type == "combines":
        # Extract tier from filename like combine-challenger-mid1385-...
        tier_match = re.search(r'combine-(\w+)-', s3_key, re.IGNORECASE)
        if tier_match:
            return f"{tier_match.group(1).capitalize()} Combines"
        return "Combines"
    return stage_type


def get_s3_prefix(season: int, stage_type: str) -> str:
    """Map stage_type to S3 prefix for listing objects."""
    if stage_type == "regulation":
        return f"s{season}/M"
    elif stage_type == "preseason":
        return f"s{season}/P"
    elif stage_type == "combines":
        return f"s{season}/Combines"
    else:
        raise ValueError(f"Unknown stage_type: {stage_type}")


def derive_filename_from_key(s3_key: str) -> str:
    """Derive the expected .dem filename from an S3 key, stripping .zip extension.
    Matches the original download script logic: join last two path parts with '-'."""
    base = '-'.join(s3_key.split('/')[-2:])
    if base.endswith('.zip'):
        base = base[:-4]
    return base


def download_and_parse(season: int, stage_type: str, connection: DbConnection, tournament: str = "CSC"):
    client = get_s3_client()
    prefix = get_s3_prefix(season, stage_type)

    response = client.list_objects(Bucket='cscdemos', Prefix=prefix)
    if 'Contents' not in response:
        print(f"No objects found for prefix {prefix}")
        return

    all_keys = [item['Key'] for item in response['Contents']]

    # Build skip sets from DB
    existing_demos = connection.list_demos()
    existing_files = {row[0] for row in existing_demos}
    existing_mids = {extract_mid(f) for f in existing_files} - {None}
    failed_files = connection.list_failed_demos(parser_version)
    failed_mids = {extract_mid(f) for f in failed_files} - {None}

    # Pre-filter keys to determine which need processing
    keys_to_process = []
    skipped_scrim = 0
    skipped_existing = 0

    for key in all_keys:
        if "Scrim" in key:
            skipped_scrim += 1
            continue

        mid = extract_mid(key)
        if mid:
            if mid in existing_mids:
                skipped_existing += 1
                continue
            if mid in failed_mids:
                skipped_existing += 1
                continue
        else:
            expected = derive_filename_from_key(key)
            if expected in existing_files or expected in failed_files:
                skipped_existing += 1
                continue

        keys_to_process.append(key)

    # Stats
    parsed = 0
    failed = 0
    skipped_demos = 0
    download_errors = 0

    print(f"\nSeason {season} {stage_type}: {len(all_keys)} total S3 keys, "
          f"{skipped_scrim} scrims ignored, {skipped_existing} already handled, "
          f"{len(keys_to_process)} to process\n")

    if not keys_to_process:
        return

    pbar = tqdm(keys_to_process, desc=f"S{season} {stage_type}", unit="zip",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}")
    pbar.set_postfix(parsed=0, failed=0, skipped=0)

    for key in pbar:
        mid = extract_mid(key)

        # Download to temp directory
        temp_dir = tempfile.mkdtemp()
        zip_filename = os.path.join(temp_dir, "demo.zip")

        try:
            with open(zip_filename, 'wb') as f:
                client.download_fileobj('cscdemos', key, f)
        except ClientError:
            download_errors += 1
            pbar.set_postfix(parsed=parsed, failed=failed, skipped=skipped_demos, dl_err=download_errors)
            shutil.rmtree(temp_dir, ignore_errors=True)
            continue

        # Extract zip
        try:
            with zipfile.ZipFile(zip_filename, 'r') as zf:
                zf.extractall(temp_dir)
        except zipfile.BadZipFile:
            download_errors += 1
            pbar.set_postfix(parsed=parsed, failed=failed, skipped=skipped_demos, dl_err=download_errors)
            shutil.rmtree(temp_dir, ignore_errors=True)
            continue

        os.remove(zip_filename)

        # Find all .dem files recursively (some zips have demos in subdirectories like demos/)
        dem_paths = []
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                if f.endswith('.dem'):
                    dem_paths.append(os.path.join(root, f))

        if not dem_paths:
            shutil.rmtree(temp_dir, ignore_errors=True)
            continue

        stage = get_stage(stage_type, key)

        for dem_path in dem_paths:
            dem_file = os.path.basename(dem_path)

            # Level 2: per-.dem skip check
            if dem_file in existing_files or dem_file in failed_files:
                skipped_demos += 1
                pbar.set_postfix(parsed=parsed, failed=failed, skipped=skipped_demos)
                continue

            success = parse_one_demo(dem_path, tournament, stage, season, connection, s3_key=key)

            if success:
                parsed += 1
                existing_files.add(dem_file)
                if mid:
                    existing_mids.add(mid)
            else:
                failed += 1
                failed_files.add(dem_file)
                if mid:
                    failed_mids.add(mid)

            pbar.set_postfix(parsed=parsed, failed=failed, skipped=skipped_demos)

        # Clean up entire temp directory (including subdirectories)
        shutil.rmtree(temp_dir, ignore_errors=True)

    pbar.close()

    print(f"\nDone: {parsed} parsed, {failed} failed, "
          f"{skipped_existing + skipped_demos} skipped, {download_errors} download errors\n")
