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

    
    