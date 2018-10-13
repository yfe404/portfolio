# coding: utf-8
import boto3 
import zipfile
import io
import mimetypes

s3 = boto3.resource('s3')
build_bucket = s3.Bucket('portfoliobuild.yannfeunteun.com')
portfolio_bucket = s3.Bucket('yannfeunteun.com')

portfolio_zip = io.BytesIO()
build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
        
with zipfile.ZipFile(portfolio_zip) as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        nm = '/'.join(nm.split('/')[1:])
        portfolio_bucket.upload_fileobj(
            obj,
            nm,
            ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0] or "text/plain"}
        )
        portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
