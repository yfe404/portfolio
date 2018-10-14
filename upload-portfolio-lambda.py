import json
import boto3                                                                                                                            import zipfile                                                                                                                          import io                                                                                                                               import mimetypes  

def lambda_handler(event, context):
    s3 = boto3.resource('s3')       
    sns = boto3.resource('sns')
    topic = sns.Topic("arn:aws:sns:eu-west-1:920313765005:deployPortfolioTopic")
    location = {
        "bucketName": "portfoliobuild.yannfeunteun.com",
        "objectKey": "portfoliobuild.zip"
    }
    
    try: 
        job = event.get("CodePipeline.job")
        
        if job: 
            for artifact in job['data']['inputArtifacts']:
                if artifact['name'] == 'BuildArtifact':
                    location = artifact['location']['s3Location']
        
        print("Building Portfolio from: {}".format(str(location)))
        build_bucket = s3.Bucket(location['bucketName'])                                                                              
        portfolio_bucket = s3.Bucket('yannfeunteun.com')                                                                              
        build_bucket.download_fileobj(location['objectKey'], portfolio_zip)

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
            
        print("Job Done!")
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully!")
        if job: 
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job['id'])
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="Portfolio deployment failure!")
        if job:
            codepipeline.put_job_failure_result(jobId=job['id'])
        raise
