import obd

def query_command(self, connection: obd.OBD ,command: obd.commands ):
        return connection.query(command)