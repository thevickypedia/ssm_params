import boto3

client = boto3.client('ssm')

response_put = client.put_parameter(
    Name='string',
    Description='string',
    Value='string',
    Type='String'|'StringList'|'SecureString',
)

print(response_put)

response_get = client.get_parameter(
    Name='string',
    WithDecryption=True|False
)

print(response_get)

response_del = client.delete_parameter(Name='string')

print(response_del)
