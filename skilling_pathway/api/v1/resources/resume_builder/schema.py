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