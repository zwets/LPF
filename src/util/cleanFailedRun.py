import os
import src.sqlCommands as sqlCommands
def clean_failed_run(arguments):
    sqlCommands.sql_update_status_table('Analysis failed', arguments.sample_name, 'Failed, log info in /opt/LPF_logs', arguments.entry_id, arguments.sql_db)