import json
import os

# PROCESSING_COMMAND = "/Users/piotr.milos/venvs/venv2.7.13/bin/python " \
#                      "~/PycharmProjects/freeplane_neptune_integration/scripts/helpers/NeptuneUIWorks.py "

PROCESSING_COMMAND = '/Users/piotr.milos/.pyenv/versions/2.7.13/bin/python /Users/piotr.milos/PycharmProjects/' \
                     'freeplane_neptune_integration/scripts/helpers/DataRetriever.py '


job_id = str(node.getAt("Neptune"))[-36:]
c.statusInfo = job_id

juggler_file = "/tmp/out2.txt"
os.system("rm {}".format(juggler_file))
os.system('touch {}'.format(juggler_file))


cmd_str = PROCESSING_COMMAND + ' --command abort_job_by_id ' \
                               '--arguments "{}" --json_output "{}"'.format(job_id,  juggler_file)


os.system(cmd_str)

with open(juggler_file, "r") as f:
    result = json.load(f)

c.statusInfo = result
