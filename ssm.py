import boto3
import logging
from pprint import pprint

client = boto3.client('ssm')


def put_param():
    name = input('Enter the name of the parameter you wish to add:\n')
    value = input(f'Enter the value for {name}:\n')
    typ = int(input('Enter the type you wish to save the parameter as:\n1. String\n2. StringList\n3. SecureString\n'))
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
        Type=typ
    )
    if response_put['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f' Parameter {name} has been ADDED successfully. Below is the response.')
    else:
        logger.info(f' Parameter {name} was not ADDED successfully. Check the response below.')
    return response_put


def get_param():
    name = input('Enter the name of the parameter you wish to retrieve (case sensitive):\n')
    response_get = client.get_parameter(Name=name, WithDecryption=True)
    param = response_get['Parameter']
    ret = {}
    name = param['Name']
    val = param['Value']
    ret[name] = val
    return ret


def delete_param():
    name = input('Enter the name of the parameter you wish to DELETE (case sensitive):\n')
    response_delete = client.delete_parameter(Name=name)

    if response_delete['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f' Parameter {name} has been DELETED successfully. Below is the response.')
    else:
        logger.info(f' Parameter {name} was not DELETED successfully. Check the response below.')

    return response_delete


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(':')
    pprint(delete_param())
