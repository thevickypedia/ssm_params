import boto3
from pprint import pprint

client = boto3.client('ssm')


def put_param():
    response_put = client.put_parameter(
        Name='name',
        Value='value',
        Type='type'
    )
    return response_put


def get_param():
    response_get = client.get_parameter(Name='name', WithDecryption=True)
    param = response_get['Parameter']
    ret = {}
    name = param['Name']
    val = param['Value']
    ret[name] = val
    return ret


def delete_param():
    response_delete = client.delete_parameter(Name='name')
    return response_delete


if __name__ == '__main__':
    pprint(delete_param())
