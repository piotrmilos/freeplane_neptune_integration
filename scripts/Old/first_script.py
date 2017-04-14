c.statusInfo = "Jython's here: Node's text is " + node.text
n = node.createChild("New experiment")
#n.attributes.set("attribute name", "12")
n.putAt("Neptune", "http://freeplane.sourceforge.net/doc/api/org/freeplane/plugin/script/proxy/Proxy.NodeRO.html#getAt-java.lang.String-")
n.style.name='experiment'
description_node = n.createChild('Description')
graph_node = n.createChild('Graph')
graph_node.setDetails("<html><head/><body><img src=/home/piotr/TMP/girl1.png></body></html>")
