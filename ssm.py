import boto3

client = boto3.client('ssm')

response = client.put_parameter(
    Name='string',
    Description='string',
    Value='string',
    Type='String'|'StringList'|'SecureString',
)

print(response)
