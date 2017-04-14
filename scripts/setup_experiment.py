import json
import os

# PROCESSING_COMMAND = "/Users/piotr.milos/venvs/venv2.7.13/bin/python " \
#                      "~/PycharmProjects/freeplane_neptune_integration/scripts/helpers/NeptuneUIWorks.py "

PROCESSING_COMMAND = '/Users/piotr.milos/.pyenv/versions/2.7.13/bin/python /Users/piotr.milos/PycharmProjects/' \
                     'freeplane_neptune_integration/scripts/helpers/DataRetriever.py '


experiment_tags = node.text

experiment_tags += " jaco"

juggler_file = "/tmp/out2.txt"
os.system("rm {}".format(juggler_file))
os.system('touch {}'.format(juggler_file))


cmd_str = PROCESSING_COMMAND + ' --command get_jobs_by_tag ' \
                               '--arguments "{}" --json_output "{}"'.format(experiment_tags,  juggler_file)


os.system(cmd_str)

with open(juggler_file, "r") as f:
    experiments = json.load(f)

node.style.name='experiment'

# experiments_names = sorted(experiments.keys())

for e in experiments:
    e_node = node.createChild(e["name"])
    e_node.putAt("Neptune", e["neptune"])
    e_node.putAt("Movies", e["movies"])
    # e_node.putAt("Id", e["id"])
#
# node.putAt("Neptune", cmd_str)
# c.statusInfo = cmd_str
