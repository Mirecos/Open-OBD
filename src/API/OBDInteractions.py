import obd

def query_command(connection: obd.OBD ,command: obd.commands ):
        return connection.query(command)