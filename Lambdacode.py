import boto3
from datetime import datetime, timedelta

# Initialize CloudWatch and SNS clients
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')

# Replace with your instance and RDS identifiers
INSTANCE_ID = 'i-0193541eaeec4d1e0'  # Your EC2 instance ID
RDS_INSTANCE_ID = 'database-1'  # Your RDS instance ID
SNS_TOPIC_ARN = 'arn:aws:sns:ap-south-1:533267114782:RDSStorageAlerts'  # Your SNS topic ARN

def get_cloudwatch_metric(namespace, metric_name, dimensions, statistic='Average'):
    response = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=datetime.utcnow() - timedelta(minutes=10),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=[statistic]
    )
    data_points = response['Datapoints']
    if data_points:
        return data_points[-1][statistic]
    return None

def lambda_handler(event, context):
    # Fetch EC2 CPU Usage
    ec2_cpu_usage = get_cloudwatch_metric(
        'AWS/EC2', 'CPUUtilization',
        [{'Name': 'InstanceId', 'Value': INSTANCE_ID}]
    )
    
    # Fetch RDS CPU Usage
    rds_cpu_usage = get_cloudwatch_metric(
        'AWS/RDS', 'CPUUtilization',
        [{'Name': 'DBInstanceIdentifier', 'Value': RDS_INSTANCE_ID}]
    )
    
    # Fetch RDS Free Storage
    rds_free_storage = get_cloudwatch_metric(
        'AWS/RDS', 'FreeStorageSpace',
        [{'Name': 'DBInstanceIdentifier', 'Value': RDS_INSTANCE_ID}]
    )
    
    # Convert free storage from bytes to GB
    rds_free_storage_gb = rds_free_storage / (1024 ** 3) if rds_free_storage else 'N/A'
    
    # Create the email body
    email_body = f"""
    Alert: RDS Storage Limit Reached!\n
    RDS Instance CPU Usage: {rds_cpu_usage:.2f}%\n
    Remaining RDS Storage: {rds_free_storage_gb:.2f} GB\n
    EC2 Instance CPU Usage: {ec2_cpu_usage:.2f}%
    """
    
    # Define RDS instance name for the subject
    rds_instance_name = RDS_INSTANCE_ID  # You can replace this with a more user-friendly name if desired
    subject = f"{rds_instance_name}, STORAGE alert: Remaining storage {rds_free_storage_gb:.2f} GB"

    # Send email via SNS
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=email_body,
        Subject=subject
    )
    
    return {
        'statusCode': 200,
        'body': 'Email sent successfully!'
    }