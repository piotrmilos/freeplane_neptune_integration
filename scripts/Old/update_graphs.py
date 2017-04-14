import json
import os

neptune_url = node.getAt("Neptune")
job_id = str(neptune_url)[47:]

c.statusInfo = "Processing:{}".format(job_id)
juggler_file = "/tmp/out2.txt"

cmd_str = 'python /home/piotr/PycharmProjects/rl2/NeptuneUIWorks.py --job_id {}' \
          ' --command graphs --arguments "{}" --json_output "{}"'.format(job_id, "/home/piotr/Dropbox/ExperimentsMaps/", juggler_file)

os.system(cmd_str)

with open(juggler_file, "r") as f:
    r = json.load(f)

c.statusInfo = "Retrived:{}".format(r)

children = node.getChildren()
for c in children:
    if c.text == "Graph":
        c.delete()

graph_node = node.createChild('Graph')
graph_node.setDetails('<html><head/><body><img src="{}"></body></html>'.format(r))

# node.putAt("Neptune", neptune_url)
# node.style.name='experiment'
# node.setText(r)
