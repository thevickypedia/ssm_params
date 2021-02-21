import logging
from pprint import pprint

import boto3


def put_param_json(name, value, typ):
    """Put parameters on ssm using json object."""
    response_put = client.put_parameter(
        Name=name,
        Value=value,
        Type=typ,
        Overwrite=True
    )
    if response_put['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f' Parameter {name} has been ADDED successfully. Below is the response.')
    else:
        logger.info(f' Parameter {name} was not ADDED successfully. Check the response below.')
    return response_put


def put_param():
    """Put parameters on ssm manually."""
    name = input('Enter the name of the parameter you wish to add:\n')
    value = input(f'Enter the value for {name}:\n')
    try:
        typ = int(
            input('Enter the type you wish to save the parameter as:\n1. String\n2. StringList\n3. SecureString\n'))
    except ValueError:
        typ = None
        logger.error(' Enter either 1 or 2 or 3, its that simple.')
        exit(1)
    if typ == 1:
        typ = 'String'
    elif typ == 2:
        typ = 'StringList'
    elif typ == 3:
        typ = 'SecureString'
    else:
        logger.error(' Enter either 1 or 2 or 3, its that simple.')
        exit(0)

    response_put = client.put_parameter(
        Name=name,
        Value=value,
        Type=typ,
        Overwrite=True
    )
    if response_put['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f' Parameter {name} has been ADDED successfully. Below is the response.')
    else:
        logger.info(f' Parameter {name} was not ADDED successfully. Check the response below.')
    return response_put


def get_param():
    """Get parameters from ssm manually."""
    name = input('Enter the name of the parameter you wish to retrieve (case sensitive):\n')
    try:
        response_get = client.get_parameter(Name=name, WithDecryption=True)
    except client.exceptions.ParameterNotFound:
        response_get = None
        logger.error(' Unable to find such a parameter or unable connect to SSM. Recheck your auth and parameter name.')
        exit(0)
    param = response_get['Parameter']
    ret = {}
    name = param['Name']
    value = param['Value']
    ret[name] = value
    return ret


def delete_param():
    """Delete parameters on ssm manually."""
    name = input('Enter the name of the parameter you wish to DELETE (case sensitive):\n')
    try:
        response_delete = client.delete_parameter(Name=name)
    except client.exceptions.ParameterNotFound:
        response_delete = None
        logger.error(' Unable to find such a parameter or unable connect to SSM. Recheck your auth and parameter name.')
        exit(0)

    if response_delete['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f' Parameter {name} has been DELETED successfully. Below is the response.')
    else:
        logger.info(f' Parameter {name} was not DELETED successfully. Check the response below.')

    return response_delete


def get_json_obj():
    """Gets the dictionary from the stored json file."""
    import json
    with open('params.json') as json_file:
        if data := json.load(json_file):
            return data


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    client = boto3.client('ssm')
    pprint(get_param())

    if content := get_json_obj():
        for key, val in content.items():
            put_param_json(name=f'/Jarvis/{key}', value=val, typ='SecureString')
            # delete_param(name=f'/Jarvis/{key}')
