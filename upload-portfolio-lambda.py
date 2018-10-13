import json
import boto3                                                                                                                            import zipfile                                                                                                                          import io                                                                                                                               import mimetypes  

def lambda_handler(event, context):
    s3 = boto3.resource('s3')       
    sns = boto3.resource('sns')
    topic = sns.Topic("arn:aws:sns:eu-west-1:920313765005:deployPortfolioTopic")
    
    try: 
        build_bucket = s3.Bucket('portfoliobuild.yannfeunteun.com')                                                                             portfolio_bucket = s3.Bucket('yannfeunteun.com')                                                                                        portfolio_zip = io.BytesIO()                                                                                                             
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:                                                                                               for nm in myzip.namelist():                                                                                                                 obj = myzip.open(nm)                                                                                                                    nm = '/'.join(nm.split('/')[1:])                                                                                                        portfolio_bucket.upload_fileobj(                                                                                                            obj,                                                                                                                                    nm,                                                                                                                                     ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0] or "text/plain"}                                                              )                                                                                                                                       portfolio_bucket.Object(nm).Acl().put(ACL='public-read')        
            
        print("Job Done!")
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully!")
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="Portfolio deployment failure!")
        raise
        


