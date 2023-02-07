import os
import src.sqlCommands as sqlCommands
def clean_failed_run(arguments):
    """Clean up failed run"""
    sqlCommands.sql_update_status_table('Analysis failed', arguments.input_file, 'Failed, log info in /opt/LPF_logs', arguments.entry_id, arguments.sql_db)