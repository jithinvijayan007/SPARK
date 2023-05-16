import json
from skilling_pathway.api.v1.resources.profile.db_connection import production_connection,dev_connection

# conn = production_connection() # production
conn = dev_connection() # dev

def callCursor():

    cursor = conn.cursor()
    query = "SELECT * FROM public.mdl_user WHERE id=2"
    cursor.execute(query)
    records = cursor.fetchall()
    print("Total number of rows in table: ", cursor.rowcount)
    return records


class GetCertificateForParticipant():
    def __init__(self, user):
        self.user = user

    def get_certificate_for_participant(self):
        cursor = conn.cursor()
        course_name = "name"
        course_full_name = "fullname"
        query = f"SELECT mu.email,mc.{course_name},mco.{course_full_name} FROM public.mdl_customcert_issues mci " \
                f"LEFT JOIN public.mdl_user mu ON mci.userid = mu.id " \
                f"LEFT JOIN public.mdl_customcert mc ON mci.customcertid = mc.id " \
                f"LEFT JOIN public.mdl_course mco ON mc.course = mco.id WHERE mu.username = %s"

        cursor.execute(query, (self.user,))
        records = cursor.fetchall()

        response = []
        for record in records:
            response.append({"email": record[0], "certificate_name": record[1],"course_name":record[2]})

        serialized_data = json.dumps(response)
        return serialized_data


class GetCousreTags():
    def __init__(self):
        pass

    def get_course_tags(self):
        curses = conn.cursor()
        tag_name ="name"
        query = f"SELECT mc.fullname,mt.{tag_name} FROM public.mdl_tag_instance mti " \
                f"LEFT JOIN public.mdl_tag mt ON mti.tagid = mt.id " \
                f"LEFT JOIN public.mdl_course mc ON mti.itemid = mc.id WHERE itemtype = 'course'";

        curses.execute(query)
        records = curses.fetchall()

        response = []
        for record in records:
            response.append({"course":record[0],"tag":record[1]})

        serialized_data = json.dumps(response)
        return serialized_data