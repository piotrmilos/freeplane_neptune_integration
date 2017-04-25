import base64
import argparse
import json

from deepsense.generated.swagger_client.apis import DefaultApi
from deepsense.generated.swagger_client import ApiClient, Experiment


def sh_escape(s):
   return s.replace("(","\\(").replace(")","\\)").replace(" ","\\ ").replace("@","\@")


def create_basic_auth_header(username, password):
    credentials = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    header_name = "Authorization"
    header_value = "Basic {}".format(credentials)
    return header_name, header_value


def create_api(username, password, rest_api_url):

    header_name, header_value = create_basic_auth_header(username, password)
    return DefaultApi(
        ApiClient(
            host=rest_api_url, header_name=header_name, header_value=header_value))


api = create_api(
    username='piotr.milos@codilime.com',
    password='plosos2n',
    rest_api_url='https://ml.neptune.deepsense.io')

URL_PREFIX = "https://ml.neptune.deepsense.io/#dashboard/job/"

def detect_host(e):
    if "piotr.milos/" in e.storage_location:
        return "past"

    return "my"



def get_jobs_by_tags(tags):
    tags_list = tags.split(" ")

    experiments = api.get_experiments(tags=tags_list)

    experiments_data = []

    for e in experiments:
        if str(e.state) == 'running':
            # e.state('aborted')
            experiment_data = {}
            experiment_data["name"] = e.name[34:]
            url_id = api.get_experiment_jobs(e.id)[0].id
            job = api.get_experiment_jobs(e.id)[0]
            url = URL_PREFIX + url_id
            experiment_data["neptune"] = url
            experiment_data["id"] = e.id
            host = detect_host(e)
            movies_command = 'cd ~/TMP && rm -rf * && scp -r "{}:{}jobs/{}/src/dumpdir/*mp4" .'.format(host,
                                                                          sh_escape(e.storage_location)[:-10],
                                                                                 url_id)
            experiment_data["movies"] = movies_command

            experiments_data.append(experiment_data)

    experiments_data = sorted(experiments_data, key=lambda x: x['name'])
    return experiments_data

def abort_jobs_by_tags(tags):
    tags_list = tags.split(" ")

    experiments = api.get_experiments(tags=tags_list)

    for e in experiments:
        if str(e.state) == 'running':
            job = api.get_experiment_jobs(e.id)[0]
            api.jobs_job_id_abort_post(job.id, x_neptune_user_role='normal_user')

    return "success"


def abort_job_by_id(id):
    api.jobs_job_id_abort_post(id, x_neptune_user_role='normal_user')

    return "success"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--job_id', help='')
    parser.add_argument('--command', help='')
    parser.add_argument('--arguments', help='')
    parser.add_argument('--json_output', help='')

    res = None

    args = parser.parse_args()

    if args.command == "get_jobs_by_tag":
        res = get_jobs_by_tags(args.arguments)

    if args.command == "abort_jobs_by_tag":
        res = abort_jobs_by_tags(args.arguments)

    if args.command == "abort_job_by_id":
        res = abort_job_by_id(args.arguments)

    if res == None:
        raise "Command {} has not been implemented.".format(args.command)

    with open(args.json_output, "w") as f:
        json.dump(res, f)

