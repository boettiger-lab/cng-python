
# upload file to huggingface
from huggingface_hub import HfApi, login
def hf_upload(file, path, repo_id = "boettiger-lab/ca-30x30", repo_type = "dataset", key = None):
    if not key:
        key = st.secrets["HF_TOKEN"]
    login(key)
    api = HfApi()
    info = api.upload_file(
            path_or_fileobj=path,
            path_in_repo=file,
            repo_id=repo_id,
            repo_type=repo_type, 
        )
        




# kinda silly.  boto3 doesn't do sync, maybe we just awscli wrap
# would be nice if source.coop supported minio client library
def s3_cp(source, 
          dest, 
          profile = "minio",
          key = "", #st.secrets["MINIO_KEY"],
          secret = "", #st.secrets["MINIO_SECRET"]
          ):
   import boto3
   from botocore.client import Config

    # assume dest is an s3_path?
    match = re.match(r'^s3://([^/]+)/(.*)$', dest)
    bucket, object_name = match.groups()
    if profile == "minio":
        s3 = boto3.client(
            "s3",
            endpoint_url = "https://minio.carlboettiger.info",
            aws_access_key_id = os.getenv("MINIO_KEY", key), 
            aws_secret_access_key = os.getenv("MINIO_SECRET", secret),
            config=Config(s3={'addressing_style': 'path'})
        )
        s3.upload_file(source, bucket, object_name)
    if profile == "sc":
        s3 = boto3.client("s3",
            endpoint_url = "https://data.source.coop",
            aws_access_key_id = os.getenv("SOURCE_KEY", key), 
            aws_secret_access_key = os.getenv("SOURCE_SECRET", secret),
            config=Config(s3={'addressing_style': 'path', 
                              'multipart_threshold': '44MB'})
        )
    s3.upload_file(source, bucket, object_name)
    



