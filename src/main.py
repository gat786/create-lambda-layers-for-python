import os
import shutil
from typing import List
from zipfile import ZipFile
import requests
import subprocess
import boto3

base_url = "https://pypi.debian.net"
bucket_name = "aws-layers-bucket"

class PackageDetail:
    def __init__(self, package_name: str, version: str) -> None:
        self.package_name = package_name
        self.version = version

    def __str__(self) -> str:
        return f"{self.package_name}-{self.version}.tar.gz"



def create_layer_with_pip(packages: List[PackageDetail]):
    """
    Create a folder named layers and inside it
    install all the dependencies using the pip cli
    in it and then create a layers.zip file depending on it
    """
    layers_folder_path = "./layers/python"
    if not os.path.exists(layers_folder_path):
        os.makedirs(layers_folder_path)
    
    for package in packages:
        subprocess.call(f"pip install {package.package_name}=={package.version} -t {layers_folder_path}".split())

    zip_file_name = "layers"
    shutil.make_archive(
        zip_file_name,
        "zip",
        f"./{zip_file_name}"
    )

def upload_layers_file_to_s3(file: str):
    s3 = boto3.client('s3')
    with open(file=file, mode='rb') as file_to_upload:
        response = s3.put_object(
            Body = file_to_upload,
            Bucket = bucket_name,
            Key = "layers.zip"
        )

        print(response)

    


def create_layer(packages: List[PackageDetail]):
    """
    Download zip files from pypi.debian.net
    and create a zip file out of it.
    """
    files = []
    for package in packages:
        url = f"{base_url}/{package.package_name}/{package}"

        try:
            package_file = requests.get(url=url)

            package_file.raise_for_status()

            files.append({
                "file_name": package.__str__(),
                "content": package_file.content
            })
        except Exception as e:
            print(f"exception occured {e}")
            pass
    
    with ZipFile('layers.zip','w') as layers_zip:
        for file in files:
            layers_zip.writestr(file['file_name'],data=file['content'])
    
    

def handler(event,context):
    print("event is ", event)
    print("context is ", context)


if __name__ == "__main__":
    packages = [
        PackageDetail("boto3", "1.26.2")
    ]

    create_layer_with_pip(packages=packages)
    # upload_layers_file_to_s3("layers.zip")
