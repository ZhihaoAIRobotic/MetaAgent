import os
from minio import Minio
from minio.error import S3Error
from datetime import timedelta
from minio.deleteobjects import DeleteObject


class Bucket(object):
    client = None
    policy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":["*"]},"Action":["s3:GetBucketLocation","s3:ListBucket"],"Resource":["arn:aws:s3:::%s"]},{"Effect":"Allow","Principal":{"AWS":["*"]},"Action":["s3:GetObject"],"Resource":["arn:aws:s3:::%s/*"]}]}'
    
    def __new__(cls, *args, **kwargs):
        if not cls.client:
            cls.client = object.__new__(cls)
        return cls.client
    
    def __init__(self, service, access_key, secret_key, secure=False):
        self.service = service
        self.client = Minio(service, access_key=access_key, secret_key=secret_key, secure=secure)

    def exists_bucket(self, bucket_name):
        """
        Check if bucket exists
        :param bucket_name: 
        :return:
        """
        return self.client.bucket_exists(bucket_name=bucket_name)
    
    def create_bucket(self, bucket_name:str, is_policy:bool=True):
        """
        Create bucket
        :param bucket_name: 
        :param is_policy: 
        :return:
        """
        if self.exists_bucket(bucket_name=bucket_name):
            return False
        else:
            self.client.make_bucket(bucket_name=bucket_name)
        if is_policy:
            policy = self.policy % (bucket_name, bucket_name)
            self.client.set_bucket_policy(bucket_name=bucket_name, policy=policy)
        return True

    def get_bucket_list(self):
        """
        list buckets
        :return:
        """
        buckets = self.client.list_buckets()
        bucket_list = []
        for bucket in buckets:
            bucket_list.append(
                {"bucket_name": bucket.name, "create_time": bucket.creation_date}
            )
        return bucket_list

    def remove_bucket(self, bucket_name):
        """
        remove bucket
        :param bucket_name:
        :return:
        """
        try:
            self.client.remove_bucket(bucket_name=bucket_name)
        except S3Error as e:
            print("[error]:", e)
            return False
        return True
    
    def bucket_list_files(self, bucket_name, prefix):
        """
        List bucket objects
        :param bucket_name: 
        :param prefix: 
        :return:
        """
        try:
            files_list = self.client.list_objects(bucket_name=bucket_name, prefix=prefix, recursive=True)
            for obj in files_list:
                print(obj.bucket_name, obj.object_name.encode('utf-8'), obj.last_modified,
                      obj.etag, obj.size, obj.content_type)
        except S3Error as e:
            print("[error]:", e)

    def bucket_policy(self, bucket_name):
        """
        Show bucket policy
        :param bucket_name:
        :return:
        """
        try:
            policy = self.client.get_bucket_policy(bucket_name)
        except S3Error as e:
            print("[error]:", e)
            return None
        return policy

    def download_file(self, bucket_name, file, file_path, stream=1024*32):
        """
        Download file and write to local path
        :return:
        """
        try:
            data = self.client.get_object(bucket_name, file)
            with open(file_path, "wb") as fp:
                for d in data.stream(stream):
                    fp.write(d)
        except S3Error as e:
            print("[error]:", e)

    def fget_file(self, bucket_name, file, file_path):
        """
        download file to local path
        :param bucket_name:
        :param file:
        :param file_path:
        :return:
        """
        self.client.fget_object(bucket_name, file, file_path)

    def copy_file(self, bucket_name, file, file_path):
        """
        copy file
        :param bucket_name:
        :param file:
        :param file_path:
        :return:
        """
        self.client.copy_object(bucket_name, file, file_path)

    def upload_file(self, bucket_name, file, file_path, content_type):
        """
        write file to bucket
        :param bucket_name: 
        :param file: file name
        :param file_path: local file path
        :param content_type: file type
        :return:
        """
        try:
            with open(file_path, "rb") as file_data:
                file_stat = os.stat(file_path)
                self.client.put_object(bucket_name, file, file_data, file_stat.st_size, content_type=content_type)
        except S3Error as e:
            print("[error]:", e)

    def fput_file(self, bucket_name, file, file_path):
        """
        Upload file
        :param bucket_name: 
        :param file: file name
        :param file_path: local file path
        :return:
        """
        try:
            self.client.fput_object(bucket_name, file, file_path)
        except S3Error as e:
            print("[error]:", e)

    def stat_object(self, bucket_name, file):
        """
        Get meta data of an object
        :param bucket_name:
        :param file:
        :return:
        """
        try:
            data = self.client.stat_object(bucket_name, file)
            print(data.bucket_name)
            print(data.object_name)
            print(data.last_modified)
            print(data.etag)
            print(data.size)
            print(data.metadata)
            print(data.content_type)
        except S3Error as e:
            print("[error]:", e)

    def remove_file(self, bucket_name, file):
        """
        Remove single file
        :return:
        """
        self.client.remove_object(bucket_name, file)

    def remove_files(self, bucket_name, file_list):
        """
        remove files
        :return:
        """
        delete_object_list = [DeleteObject(file) for file in file_list]
        for del_err in self.client.remove_objects(bucket_name, delete_object_list):
            print("del_err", del_err)

    def presigned_get_file(self, bucket_name, file, days=7):
        """
        Generate a http URL
        :return:
        """
        return self.client.presigned_get_object(bucket_name, file, expires=timedelta(days=days))


MINIO_OBJ = Bucket(service="192.168.0.20:9000", access_key="minioadmin:minioadmin", secret_key="minioadmin:minioadmin", secure=False)
MINIO_OBJ.create_bucket(bucket_name="cartoonist")
