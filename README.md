# ☁️ SafeCloud Scanner

Simple hands-on AWS project that scans uploaded files using VirusTotal.  
Files uploaded to a staging S3 bucket are scanned automatically by Lambda, then moved to either a Safe or Malicious bucket. You get an SNS email with the result.  
This is small, clean, and made for learning cloud automation and security.

---

## ✨ At a glance

**Upload → S3 (staging) → Lambda → VirusTotal → Safe / Malicious S3 → SNS email**

---

## 🔑 Features

- Event-driven: S3 upload triggers Lambda  
- VirusTotal integration for scanning  
- Files stored separately (safe / malicious)  
- Email notifications with SNS  
- Minimal, easy-to-follow setup

---

##  💻 Setup

**1) Create S3 buckets 🪣**

```bash
aws s3 mb s3://my-staging-bucket-123
aws s3 mb s3://my-safe-bucket-123
aws s3 mb s3://my-malicious-bucket-123
```

Create three buckets: staging (uploads), safe (clean files), malicious (infected files). Use unique names.

---

**2) Create SNS topic and subscribe your email**

```bash
aws sns create-topic --name FileScanResults
aws sns subscribe \
  --topic-arn arn:aws:sns:REGION:ACCOUNT_ID:FileScanResults \
  --protocol email \
  --notification-endpoint youremail@example.com
```

Confirm the subscription link you get by email.

---

**3) Create Lambda and upload code**

Upload `lambda/scan_file.py` to a new Lambda function.  
Add environment variables inside Lambda:

```
VIRUSTOTAL_API_KEY=<your_api_key>
SAFE_BUCKET=my-safe-bucket-123
MALICIOUS_BUCKET=my-malicious-bucket-123
SNS_TOPIC_ARN=arn:aws:sns:REGION:ACCOUNT_ID:FileScanResults
```

Keep the API key secret (don’t commit it). For better security, use AWS Secrets Manager.

---

**4) Attach IAM role / minimal policy to Lambda**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:HeadObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-staging-bucket-123/*",
        "arn:aws:s3:::my-safe-bucket-123/*",
        "arn:aws:s3:::my-malicious-bucket-123/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:REGION:ACCOUNT_ID:FileScanResults"
    }
  ]
}
```

Attach this role to Lambda so it can read from staging, write to results, and publish SNS.

---

**5) Add S3 trigger (staging bucket)**

In the S3 console (or Lambda triggers), add an event notification on the staging bucket for `ObjectCreated` to invoke your Lambda. Now every upload runs the scanner.

just go to lambda function add the trigger and select S3 in it and choose your bucket and use eventa as `AllObjectCreateEvvent` and click add.

---



After upload:
- Lambda runs and scans the file  
- File moves to safe or malicious bucket  
- You get an SNS email with the result  
- Check CloudWatch logs for details

---

## 🛠 Troubleshooting (quick)

- Lambda not triggered → check S3 event notification config  
- No email → confirm SNS subscription link in email  
- VirusTotal errors → check API key and rate limit (logs in CloudWatch)  
- Access denied → update IAM policy and ARNs

---

## 🧾 Author

MIT License  

Made by **Ridam Darji** — simple, practical cloud security projects.  

---
