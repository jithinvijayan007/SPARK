import psycopg2
import sshtunnel

def production_connection():
    ssh_host = 'ec2-3-111-127-186.ap-south-1.compute.amazonaws.com'
    ssh_port = 22
    ssh_username = 'ubuntu'
    ssh_pem_key_path = 'moodle.pem'

    database_host = 'moodle.cu3aqkf2pmm4.ap-south-1.rds.amazonaws.com'
    database_port = 5432
    database_username = 'moodle_user'
    database_password = '7j3rqck39W94jHMTSA92uSy43h7xoV9h'

    # Establish the connection

    tunnel = sshtunnel.SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_pkey=ssh_pem_key_path,
        remote_bind_address=(database_host, database_port)
    )

    tunnel.start()

    conn = psycopg2.connect(
        user=database_username,
        password=database_password,
        host='127.0.0.1',
        port=tunnel.local_bind_port,
        database='moodle_db'
    )
    return conn

def dev_connection():
    database_host = '52.66.236.159'
    database_port = 5438
    database_username = 'moodle_user'
    database_password = '7j3rqck39W94jHMTSA92uSy43h7xoV9h'

    conn = psycopg2.connect(
        user=database_username,
        password=database_password,
        host=database_host,
        port= database_port,
        database='moodle_db'
    )

    return conn