import json
import logging
import os
import time
from typing import NoReturn, Tuple, AnyStr, Iterable

import boto3
from boto3 import client

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(fmt=logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s',
    datefmt='%b-%d-%Y %I:%M:%S %p'
))
logger.addHandler(hdlr=handler)
logger.setLevel(level=logging.DEBUG)

session = boto3.Session(aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                        region_name=os.environ.get('AWS_REGION_NAME', 'us-west-2'))
ssm_client = session.client(service_name='ssm')


def get_resources(ssm_details: dict) -> Tuple[list, AnyStr]:
    """Get SSM resources along with the token for next parameter."""
    results = ssm_details['Parameters']
    resources = [result for result in results]
    next_token = ssm_details.get('NextToken', None)
    return resources, next_token


def get_all_params(boto3_client: client = ssm_client, incl_value: bool = True) -> Iterable[dict]:
    """Yields all the SSM parameters as a dictionary."""
    next_token = ''
    while next_token is not None:
        ssm_details = boto3_client.describe_parameters(MaxResults=50, NextToken=next_token)
        current_batch, next_token = get_resources(ssm_details)
        for r in current_batch:
            if incl_value:
                yield_ = dict(Name=r.get('Name'), Type=r.get('Type'),
                              Value=get_param_value(name=r.get('Name'), boto3_client=boto3_client),
                              Description=r.get('Description', f"Parameter for the key {r.get('Name').split('/')[-1]}"))
            else:
                yield_ = dict(Name=r.get('Name'), Type=r.get('Type'),
                              Description=r.get('Description', f"Parameter for the key {r.get('Name').split('/')[-1]}"))
            yield yield_


def dump_all_params(filename: str):
    """Dump all the parameters in a JSON file."""
    data = list(get_all_params())
    logger.info("Total number of parameters found: %s" % len(data))
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def put_param(name: str, value: str, param_type: str, description: str, boto3_client: client = ssm_client) -> NoReturn:
    """Put parameters on ssm manually."""
    response_put = boto3_client.put_parameter(
        Name=name,
        Value=value,
        Type=param_type,
        Description=description,
        Overwrite=True
    )
    if response_put['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f'Parameter {name!r} has been ADDED successfully to {boto3_client.meta.region_name!r}')
    else:
        logger.error('Parameter %s was NOT ADDED.' % name)
        logger.error(response_put)


def get_param_value(name: str, boto3_client: client = ssm_client):
    """Get parameters from ssm manually."""
    try:
        return boto3_client.get_parameter(Name=name, WithDecryption=True).get('Parameter', {}).get('Value')
    except boto3_client.exceptions.ParameterNotFound as error:
        logger.error(error)


def delete_param(name: str, boto3_client: client = ssm_client):
    """Delete parameters on ssm manually."""
    try:
        response_delete = boto3_client.delete_parameter(Name=name)
    except boto3_client.exceptions.ParameterNotFound as error:
        logger.error(error)
        return

    if response_delete['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f'Parameter {name!r} has been DELETED successfully from {boto3_client.meta.region_name!r}')
    else:
        logger.error('Parameter %s was NOT DELETED.' % name)
        logger.error(response_delete)


def delete_param_regex(looks_like: str, boto3_client: client = ssm_client) -> NoReturn:
    """Delete parameters that match the name."""
    for param in get_all_params(boto3_client=boto3_client, incl_value=False):
        if looks_like in param.get('Name'):
            logger.info(f"Deleting the parameter {param.get('Name')!r} from {boto3_client.meta.region_name!r}.")
            time.sleep(1)
            delete_param(name=param.get('Name'), boto3_client=boto3_client)


def swap_regions(from_, to_, delete_src: bool = True) -> NoReturn:
    """Move/copy parameters from one region to another."""
    available_regions = session.get_available_regions(service_name='ssm')
    if from_ not in available_regions or to_ not in available_regions:
        raise ValueError(f"Pick a region that is available.\nAvailable regions: {available_regions}")
    client_from = session.client(service_name='ssm', region_name=from_)
    client_to = session.client(service_name='ssm', region_name=to_)
    for param in get_all_params(boto3_client=client_from):
        logger.info(f"Got parameter {param.get('Name')!r} from {from_!r}")
        put_param(name=param.get('Name'), param_type=param.get('Type'), value=param.get('Value'),
                  description=param.get('Description'), boto3_client=client_to)
        if delete_src:
            delete_param(name=param.get('Name'), boto3_client=client_from)
