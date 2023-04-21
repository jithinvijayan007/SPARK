from skilling_pathway.db_session import session
from skilling_pathway.models.resume_builder import ResumeBuilder

def insert_resume_data(data):
    try:
        data.pop('access-token')
        data['name'] = data.pop('full_name')
        data['education_qualification'] = data.pop('educational_qualification')
        data['work_experience'] = data.pop('work_experiance')
        data['certification'] = data.pop('certifications')
        resume = ResumeBuilder(**data)
        session.add(resume)
        session.commit()
        return {
            "status": True, 
            "message": "Resume Created Successfully",
            'data':[{'id':str(resume.id)}]    
            }, 200
    except Exception as e:
            session.rollback()
            session.commit()
            return {
                "status": False,
                "message": "Something went wrong",
                "error": str(e),
            }, 500
            

def get_resume_details(data):
    try:
        resume_obj = session.query(ResumeBuilder).filter(ResumeBuilder.id==data.get('id')).\
            order_by(ResumeBuilder.created_at.desc()).first()
        if resume_obj:
            return {
                    'id':str(resume_obj.id),
                    'full_name':resume_obj.name,
                    'current_address':resume_obj.current_address,
                    'educational_qualification':resume_obj.education_qualification,
                    'skills':resume_obj.skills,
                    'work_experience':resume_obj.work_experience,
                    'gender':resume_obj.gender,
                    'email':resume_obj.email
                    
            }
        
    
    except Exception as e:
        session.rollback()
        session.commit()
        return {
                "status": False,
                "message": "Something went wrong",
                "error": str(e),
            }, 500
'''
   
    name = Column(TEXT)
    mobile = Column(String(15),nullable=True)
    email  = Column(String(15),nullable=True)
    # gender = Column(String(5),nullable=True)
    current_address = Column(TEXT, nullable=True)
    education_qualification = Column(ARRAY(String), nullable=True)
    skills = Column(ARRAY(String), nullable=True)
    work_experience = Column(JSON,nullable=True)
    certification = Column(ARRAY(UUID),nullable=True)
    # other_certifications = Column(JSON,nullable=True)
    is_active = Column(Boolean,default=True)
    created_by = Column(UUID, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

'''


ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


import os
from werkzeug.utils import secure_filename
import boto3
import mimetypes

def upload_file_to_s3(file, acl="public-read"):
    filename = secure_filename(file.name)

    content_type = mimetypes.guess_type(file.name)
    s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv('AWS_S3_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_S3_SECRET_ACCESS_KEY')
        )
    try:
        s3.upload_fileobj(
            file,
            os.getenv("AWS_S3_BUCKET_NAME"),
            f"{file.name}",
            ExtraArgs={
                "ACL": acl,
                "ContentType": content_type[0]
            }
        )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    

    # after upload file to s3 bucket, return filename of the uploaded file
    return file.name


def upload_file_to_s3_textract(file, acl="public-read"):
    filename = secure_filename(file.filename)
    s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv('AWS_S3_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_S3_SECRET_ACCESS_KEY')
        )
    try:
        s3.upload_fileobj(
            file,
            os.getenv("AWS_S3_BUCKET_NAME"),
            f"resume/{file.filename}",
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    

    # after upload file to s3 bucket, return filename of the uploaded file
    return file.filename