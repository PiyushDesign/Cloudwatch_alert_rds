
# AWS Setup for RDS Storage Alerts and EC2 Monitoring

## Step 1: Create RDS MariaDB Instance

```bash
# Command to create an RDS MariaDB instance
aws rds create-db-instance \
    --db-instance-identifier my-mariadb-instance \
    --db-instance-class db.t3.micro \
    --engine mariadb \
    --master-username admin \
    --master-user-password yourpassword \
    --allocated-storage 20 \
    --storage-type gp2
```

## Step 2: Create EC2 Instance

```bash
# Command to create an EC2 instance
aws ec2 run-instances \
    --image-id ami-12345678 \  # Replace with a valid AMI ID
    --count 1 \
    --instance-type t2.micro \
    --key-name your-key-pair \
    --security-group-ids sg-12345678 \  # Replace with your security group ID
    --subnet-id subnet-12345678  # Replace with your subnet ID
```

## Step 3: Set Up CloudWatch Alerts

### Metric Selection

- **FreeStorageSpace**: This metric indicates the available storage in bytes for your RDS instance. 

### Threshold Definition

- **Threshold**: Set an alarm to trigger when the free storage drops below 17 GB.
- **Calculation**: 17 GB in bytes is calculated as:
  \[
  17 \times 1024^3 = 18,201,648,640 \text{ bytes}
  \]

### Alarm Configuration

```bash
# Command to create a CloudWatch alarm for RDS FreeStorageSpace
aws cloudwatch put-metric-alarm \
    --alarm-name RDSFreeStorageSpaceAlarm \
    --metric-name FreeStorageSpace \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 18253611008 \  # 17 GB in bytes
    --comparison-operator LessThanThreshold \
    --dimensions Name=DBInstanceIdentifier,Value=my-mariadb-instance \
    --alarm-actions arn:aws:sns:your-region:your-account-id:your-sns-topic \
    --unit Bytes
```

## Step 4: Create Lambda Function

### Create Lambda Function

``` sh
Check the Code in `Lamdacode.py`

```

## Step 5: Create SNS Topic

### Create SNS Topic

```bash
# Command to create an SNS topic
aws sns create-topic --name my-sns-topic
```

### Subscribe to SNS Topic

```bash
# Command to subscribe your email to the SNS topic
aws sns subscribe \
    --topic-arn arn:aws:sns:your-region:your-account-id:my-sns-topic \
    --protocol email \
    --notification-endpoint your-email@example.com
```

---
