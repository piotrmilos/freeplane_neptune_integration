import argparse
import json
import os
import random

import requests
from requests.auth import HTTPBasicAuth
from easydict import EasyDict as edict
# import matplotlib.pyplot as plt
import numpy as np
# import seaborn as sns
# from region import Region


class NeptuneService(object):

    def __init__(self, region, neptune_instance):
        self._region = region
        self.neptune_instance = neptune_instance
        self._api_version = None #type: str


    # def get_jobs(self, neptune_instance):
    #     url = self._get_url_jobs(neptune_instance)
    #     print str(neptune_instance)
    #     resp = requests.get(url, auth=HTTPBasicAuth(neptune_instance.user, neptune_instance.password))
    #     if resp.status_code == 200:
    #         return resp.json()
    #     else:
    #         raise Exception("Unexpected StatusCode: " + str(resp.status_code))

    def get_job(self, job_id):
        url = self._get_base_url() + self._get_path("/default/jobs/{}".format(job_id))
        print(url)
        resp = requests.get(url, auth=HTTPBasicAuth(neptune_instance.user, neptune_instance.password))
        if resp.status_code == 200:
            return edict(resp.json())
        else:
            raise Exception("Unexpected StatusCode: " + str(resp.status_code))

    def get_channel_values(self, job_id, channel_id):
        url = self._get_base_url() + self._get_path("/default/jobs/{}/"
                                               "channels/values?channelIds={}".format(job_id, channel_id))
        print(url)
        resp = requests.get(url, auth=HTTPBasicAuth(neptune_instance.user, neptune_instance.password))
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception("Unexpected StatusCode: " + str(resp.status_code))


    def _get_base_url(self):
        return "https://" + self.neptune_instance.instance_name + \
               "." + self._get_hostname_suffix()

    def _get_url_jobs(self):
        return self._get_base_url(self.neptune_instance) + self._get_path(self.neptune_instance, "/default/jobs")

    def _get_hostname_suffix(self):
        if self._region == "EUROPE":
            return "neptune.deepsense.io/"
        elif self._region == "US":
            return "neptune-us.deepsense.io/"
        else:
            raise Exception("Unknown region " + self._region)

    def _get_api_version(self):
        # self._api_version = "1.4"
        if self._api_version == None:
            url = self._get_base_url() + 'version'
            resp = requests.get(url, auth=HTTPBasicAuth(self.neptune_instance.user, self.neptune_instance.password))
            if resp.status_code == 200:
                full_version = resp.json()['version'].split(".")
                first_two_digits = full_version[0:2]
                self._api_version = ".".join(first_two_digits)
            else:
                raise Exception("Unexpected StatusCode: " + str(resp.status_code))
        return self._api_version


    def _get_path(self, command):
        return self._get_api_version() + command



    @staticmethod
    def channel_data_to_numpy(channel_data):
        if len(channel_data) != 0:
            l = map(lambda x:x["y"]["numericValue"], channel_data[0]["values"])
            return np.array(l)
        else:
            return np.array([])

    def get_graphs(self, r, dump_dir):
        mean_channel_id = ""
        max_channel_id = ""
        std_channel_id = ""

        for c in r["channels"]:
            if c["name"] == "mean_score":
                mean_channel_id = c["id"]
            if c["name"] == "max_score":
                max_channel_id = c["id"]
            if c["name"] == "std_of_score":
                std_channel_id = c["id"]

        r = self.get_channel_values(job_id, mean_channel_id)
        mean_data = self.channel_data_to_numpy(r)
        print mean_data

        r = self.get_channel_values(job_id, std_channel_id)
        std_data = 0.5*self.channel_data_to_numpy(r)
        print std_data

        r = self.get_channel_values(job_id, max_channel_id)
        max_data = self.channel_data_to_numpy(r)
        print std_data


        sns.set(style="darkgrid")


        data_down = mean_data - std_data
        data_up = mean_data + std_data
        data = np.stack((data_down, data_up))

        if data.shape[1] >0:
            sns.tsplot(data=data,  err_style="ci_bars")
            sns.tsplot(data=max_data, color=sns.xkcd_rgb["pale red"])

            r_int = random.randint( 100000, 900000)
            file_name = "{}.png".format(r_int)
            path = os.path.join(dump_dir, file_name)
            plt.savefig(path)

            return path
        else:
            return ""

    def graph_data(self, r, channel_name):
        channel_id = ""

        for c in r["channels"]:
            if c["name"] == channel_name:
                channel_id = c["id"]


        r = self.get_channel_values(job_id, channel_id)

        data = self.channel_data_to_numpy(r)
        # print "Data:{}".format(data.tolist())
        return data.tolist()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--job_id', help='')
    parser.add_argument('--command', help='')
    parser.add_argument('--arguments', help='')
    parser.add_argument('--json_output', help='')

    args = parser.parse_args()

    ns = {}
    ns["user"] = os.environ["NEPTUNE_USER"]
    ns["password"] = os.environ["NEPTUNE_PASSWORD"]
    ns["instance_name"] = "ml"
    ns = edict(ns)
    #
    # str = "https://ml.neptune.deepsense.io/#dashboard/job/511dcb28-399a-4cf7-9d63-5856406734df"

    job_id = args.job_id

    # job_id = "472e46f6-fdd8-4a49-9b8b-721a04bd4cd6"

    neptune_instance = edict(ns)
    neptune_service = NeptuneService("EUROPE", ns)

    res = None

    if args.command == "name":
        r = neptune_service.get_job(job_id)
        res = r.name

    if args.command == "graphs":
        r = neptune_service.get_job(job_id)
        # res = neptune_service.get_graphs(r, "/tmp")
        res = neptune_service.get_graphs(r, args.arguments)

    if args.command == "graphdata":
        r1 = neptune_service.get_job(job_id)
        # print "R1:{}".format(1)
        r2 = neptune_service.graph_data(r1, args.arguments)

        res = (r1.name, r2)



    if res == None:
        raise "Command {} has not been implemented.".format(args.command)

    with open(args.json_output, "w") as f:
        json.dump(res, f)




