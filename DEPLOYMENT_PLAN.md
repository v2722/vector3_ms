# Deployment Plan — Portfolio Manager (AWS)

## Architecture Overview

```
                              ┌──────────────────────┐
                              │   Route 53 (Domain)   │
                              └──────┬───────────────┘
                                     │
                      ┌──────────────┴──────────────┐
                      │       CloudFront (CDN)       │
                      └──────┬──────────────┬───────┘
                             │              │
                    ┌────────┘              └────────┐
                    ▼                                 ▼
          ┌─────────────────┐          ┌──────────────────────┐
          │  S3 Bucket       │          │  Elastic Beanstalk   │
          │  (React/Vue SPA) │          │  (FastAPI Docker)    │
          └─────────────────┘          └──────────┬───────────┘
                                                  │
                    ┌─────────────────────────────┐│
                    │  Lambda (Daily Ingestion)    ││
                    │  - yfinance price fetch      ││
                    │  - portfolio valuation       ││
                    └──────────┬──────────────────┘│
                               │                   │
                               └───────┬───────────┘
                                       │
                                       ▼
                            ┌──────────────────┐
                            │  RDS MySQL        │
                            │  (Managed DB)     │
                            └──────────────────┘
```

| Component | AWS Service | Purpose |
|-----------|-------------|---------|
| Backend API | Elastic Beanstalk (Docker) | FastAPI application |
| Frontend | S3 + CloudFront | Static SPA hosting |
| Database | RDS MySQL | Persistent storage |
| Scheduled Task | Lambda + EventBridge | Daily price ingestion |
| CI/CD | GitHub Actions | Automated deploy pipeline |

---

## Phase 0: Prerequisites

### 0.1 IAM User Setup
- Create an IAM user with programmatic access
- Attach policies:
  - `AdministratorAccess-AWSElasticBeanstalk`
  - `AmazonS3FullAccess`
  - `CloudFrontFullAccess`
  - `AmazonRDSFullAccess`
  - `AWSLambda_FullAccess`
  - `AmazonEventBridgeFullAccess`
  - `AmazonEC2ContainerRegistryFullAccess`
- Save Access Key ID + Secret Access Key for CLI

### 0.2 AWS CLI + EB CLI
```bash
aws configure          # enter access key, secret key, region (us-east-1)
pip install awsebcli   # EB CLI
```

### 0.3 Git Repository
Make sure everything is committed:
```bash
git add .
git commit -m "pre-deployment snapshot"
```

---

## Phase 1: Database — RDS MySQL

### 1.1 Provision RDS

**Console or CLI:**
```bash
aws rds create-db-instance \
  --db-instance-identifier portfolio-manager-db \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password <secure-password> \
  --allocated-storage 20 \
  --publicly-accessible false \
  --vpc-security-group-ids sg-xxxxxxxx
```

**Recommended settings:**
- Engine: MySQL 8.0
- Class: `db.t3.micro` (free tier eligible)
- Storage: 20 GB gp2
- Public access: **No** (EB connects privately via security group)
- Automated backups: Enabled (7-day retention)

### 1.2 Security Group
- Create security group for RDS
- Inbound rule: MySQL/Aurora (3306) from **EB security group** only (not `0.0.0.0/0`)

### 1.3 Initialize Schema

Connect from a jumpbox EC2 or local machine (with VPN/SG access):
```bash
mysql -h <rds-endpoint> -u admin -p
```

Run your schema scripts (`app/database/init_db.sql`, `app/database/seed_data.sql`):
```sql
CREATE DATABASE portfolio_manager;
USE portfolio_manager;
-- run init_db.sql content here
-- run seed_data.sql content here
```

### 1.4 Note the RDS Endpoint
```
portfolio-manager-db.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com
```

---

## Phase 2: Backend — Dockerize + Elastic Beanstalk

### 2.1 Create Dockerfile

**File:** `vector3_ms/portfolio_manager/Dockerfile`

```dockerfile
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Note:** TensorFlow has a large image size (~1.5 GB+). If you want faster deployments and Lambda for ingestion, consider:
- **Option A:** Keep TF in API. Use `python:3.13-slim` + install TF. Expect 2-3 min cold starts.
- **Option B:** Move ML endpoints to a separate Lambda or SageMaker. Keep API lightweight.
- **Option C:** Use `tensorflow-cpu` and `--no-cache-dir` to reduce size.

Recommended for now: **Option A** with increased EB instance size.

### 2.2 Create Docker Ignore

**File:** `vector3_ms/portfolio_manager/.dockerignore`

```
venv/
__pycache__/
*.pyc
*.pyo
.env
.git
.gitignore
*.md
.vscode/
.idea/
*.png
*.PNG
```

### 2.3 Create EB Config Files

**File:** `vector3_ms/portfolio_manager/Procfile`

```
web: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**File:** `vector3_ms/portfolio_manager/Dockerrun.aws.json`

```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "portfolio-manager-api:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": 8000,
      "HostPort": 8000
    }
  ],
  "Logging": "/var/log/nginx",
  "Authentication": {
    "Bucket": "elasticbeanstalk-us-east-1-<account-id>",
    "Key": "dockercfg.json"
  }
}
```

**File:** `vector3_ms/portfolio_manager/.ebignore`

```
venv/
__pycache__/
*.pyc
.env
.git
.vscode/
.idea/
*.png
*.PNG
*.md
```

### 2.4 Create EB Environment

```bash
cd vector3_ms/portfolio_manager

# Initialize EB application
eb init portfolio-manager-api \
  --platform docker \
  --region us-east-1

# Create environment (this provisions EC2 + ELB + SG)
eb create portfolio-manager-prod \
  --instance-type t3.small \
  --service-role aws-elasticbeanstalk-service-role \
  --envvars "DB_HOST=<rds-endpoint>,DB_USER=admin,DB_PASS=<password>,DB_NAME=portfolio_manager,JWT_SECRET=<generate-secret>,JWT_ALGORITHM=HS256,JWT_EXPIRATION_HOURS=24,ALPHA_VANTAGE_API_KEY=<key>,FINNHUB_API_KEY=<key>"
```

### 2.5 EB Environment Configuration

After creation, customize via `eb config`:

- **Health check path:** `/`
- **Rolling updates:** `Rolling` (not `All at once`)
- **EC2 security group:** Allow inbound 8000 from ELB
- **RDS SG:** Add inbound rule for EB EC2 SG on port 3306
- **Environment type:** `Load balanced` (for production)
- **Min instances:** 1, **Max instances:** 2 (or higher)

### 2.6 Verify Deployment

```bash
eb status         # get environment URL
curl http://portfolio-manager-prod.eba-xxx.us-east-1.elasticbeanstalk.com/
```

Expected: `{"message":"Portfolio Manager API is running"}`

---

## Phase 3: Daily Ingestion — Lambda + EventBridge

The existing `scripts/daily_ingestion.py` calls:
- `ingest_daily_prices()` — fetches yfinance prices for all assets
- `update_portfolio_valuations()` — recalculates portfolio performance

### 3.1 Lambda Function Code

**File:** `vector3_ms/lambda/daily_ingestion/lambda_function.py`

```python
import sys
import os
import json
import mysql.connector
import yfinance as yf
from datetime import datetime, timedelta

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]

def get_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def ingest_daily_prices():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT ticker FROM asset")
    tickers = [row["ticker"] for row in cursor.fetchall()]
    cursor.close()
    db.close()

    if not tickers:
        print("No assets found in database")
        return

    for ticker in tickers:
        try:
            data = yf.download(ticker, period="2d", interval="1d")
            if data.empty:
                continue
            latest = data.iloc[-1]
            db = get_db()
            cursor = db.cursor()
            sql = """
                INSERT INTO price_history (ticker, date, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE open=%s, high=%s, low=%s, close=%s, volume=%s
            """
            vals = (
                ticker, latest.name.date(),
                float(latest["Open"]), float(latest["High"]),
                float(latest["Low"]), float(latest["Close"]),
                int(latest["Volume"]),
                float(latest["Open"]), float(latest["High"]),
                float(latest["Low"]), float(latest["Close"]),
                int(latest["Volume"])
            )
            cursor.execute(sql, vals)
            db.commit()
            cursor.close()
            db.close()
            print(f"✓ {ticker} updated")
        except Exception as e:
            print(f"✗ Error fetching {ticker}: {e}")

    print("Daily price ingestion complete")

def update_portfolio_valuations():
    # Simplified version of your existing update_portfolio_valuations()
    # Same logic as scripts/daily_ingestion.py
    # (Copy the full function from the existing file)
    pass

def lambda_handler(event, context):
    print(f"Starting daily ingestion at {datetime.now()}")
    ingest_daily_prices()
    update_portfolio_valuations()
    print(f"Completed at {datetime.now()}")
    return {"statusCode": 200, "body": json.dumps("OK")}
```

### 3.2 Lambda Deployment Package

**Option A — Zip upload (for dependencies under 250 MB):**

```bash
cd vector3_ms/lambda/daily_ingestion
pip install yfinance mysql-connector-python -t .
zip -r lambda_package.zip . -x "*.pyc" -x "__pycache__/*"
aws lambda create-function \
  --function-name portfolio-daily-ingestion \
  --runtime python3.13 \
  --role arn:aws:iam::<account-id>:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_package.zip \
  --timeout 300 \
  --memory-size 512 \
  --vpc-config SubnetIds=<subnet-1>,<subnet-2>,SecurityGroupIds=<sg-rds-access>
```

**Option B — Docker image (recommended for yfinance + TF dependencies):**

**File:** `vector3_ms/lambda/daily_ingestion/Dockerfile`

```dockerfile
FROM public.ecr.aws/lambda/python:3.13

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lambda_function.py .

CMD ["lambda_function.lambda_handler"]
```

Build & push:
```bash
cd vector3_ms/lambda/daily_ingestion
aws ecr create-repository --repository-name portfolio-daily-ingestion
docker build -t portfolio-daily-ingestion .
docker tag portfolio-daily-ingestion:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/portfolio-daily-ingestion:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/portfolio-daily-ingestion:latest

aws lambda create-function \
  --function-name portfolio-daily-ingestion \
  --package-type Image \
  --code ImageUri=<account-id>.dkr.ecr.us-east-1.amazonaws.com/portfolio-daily-ingestion:latest \
  --role arn:aws:iam::<account-id>:role/lambda-execution-role \
  --timeout 300 \
  --memory-size 512 \
  --vpc-config SubnetIds=<subnet-1>,<subnet-2>,SecurityGroupIds=<sg-rds-access>
```

### 3.3 Lambda Execution Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability"
      ],
      "Resource": "arn:aws:ecr:*:*:repository/portfolio-daily-ingestion"
    }
  ]
}
```

### 3.4 Schedule — EventBridge

```bash
aws events put-rule \
  --name portfolio-daily-ingestion-schedule \
  --schedule-expression "cron(0 14 * * ? *)"   # 14:00 UTC = 10:00 AM ET

aws events put-targets \
  --rule portfolio-daily-ingestion-schedule \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:<account-id>:function:portfolio-daily-ingestion"
```

### 3.5 Environment Variables

Set in Lambda console or CLI:
```
DB_HOST=<rds-endpoint>
DB_USER=admin
DB_PASS=<password>
DB_NAME=portfolio_manager
```

### 3.6 Lambda Security Group
- Lambda must be in the same VPC as RDS (or VPC-peered)
- SG must allow outbound MySQL (3306) to RDS SG
- Lambda **must** have Internet access via NAT Gateway to reach yfinance API (or use a VPC endpoint + public subnet for yfinance calls)

**Critical:** If Lambda is in a private VPC, it cannot reach `yfinance` (external API). Solutions:
1. Place Lambda in a **public subnet** with an Elastic IP
2. Place Lambda in a **private subnet** with a **NAT Gateway** in a public subnet
3. Use a **VPC endpoint** for yfinance (not possible — yfinance is external)
4. Use **Lambda function URL** + **CloudFront** as proxy (over-engineered)

**Recommendation:** Deploy Lambda in a private subnet with a NAT Gateway for outbound internet.

---

## Phase 4: Frontend — S3 + CloudFront

### 4.1 Create Frontend App

If using React:
```bash
npx create-react-app dashboard
cd dashboard
npm install axios react-router-dom chart.js
```

Configure API base URL in `.env`:
```
REACT_APP_API_URL=https://api.yourdomain.com
```

### 4.2 Build

```bash
npm run build
# Output in build/
```

### 4.3 Create S3 Bucket

```bash
aws s3 mb s3://portfolio-manager-dashboard --region us-east-1
aws s3 website s3://portfolio-manager-dashboard \
  --index-document index.html \
  --error-document index.html
```

Block public access: **OFF** (for static website hosting) OR use OAC (Origin Access Control) with CloudFront.

### 4.4 Upload Build

```bash
aws s3 sync build/ s3://portfolio-manager-dashboard/ --delete
```

### 4.5 CloudFront Distribution

```bash
aws cloudfront create-distribution \
  --origin-domain-name portfolio-manager-dashboard.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html \
  --enabled
```

**Custom error response:** Configure 403/404 to return `/index.html` (for SPA routing).

### 4.6 Custom Domain + SSL (Optional)

1. Request ACM certificate in `us-east-1`
2. Create CloudFront distribution with:
   - Alternate domain: `dashboard.yourdomain.com`
   - SSL certificate: ACM cert
3. Create Route 53 A-record alias pointing to CloudFront

### 4.7 API CORS

Update FastAPI to allow CloudFront origin in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Phase 5: CI/CD Pipeline — GitHub Actions

### 5.1 GitHub Secrets

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | `us-east-1` |
| `EB_ENV_NAME` | `portfolio-manager-prod` |
| `EB_APP_NAME` | `portfolio-manager-api` |
| `S3_BUCKET` | `portfolio-manager-dashboard` |
| `CF_DISTRIBUTION_ID` | CloudFront distribution ID |
| `LAMBDA_FUNCTION_NAME` | `portfolio-daily-ingestion` |

### 5.2 Workflow File

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  # ─── BACKEND: Deploy to Elastic Beanstalk ───
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push Docker image to ECR
        working-directory: vector3_ms/portfolio_manager
        run: |
          IMAGE_TAG=${{ github.sha }}
          docker build -t ${{ secrets.EB_APP_NAME }}:$IMAGE_TAG .
          docker tag ${{ secrets.EB_APP_NAME }}:$IMAGE_TAG \
            ${{ steps.login-ecr.outputs.registry }}/${{ secrets.EB_APP_NAME }}:$IMAGE_TAG
          docker push ${{ steps.login-ecr.outputs.registry }}/${{ secrets.EB_APP_NAME }}:$IMAGE_TAG
          echo "image=${{ steps.login-ecr.outputs.registry }}/${{ secrets.EB_APP_NAME }}:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Generate Dockerrun.aws.json
        working-directory: vector3_ms/portfolio_manager
        run: |
          cat > Dockerrun.aws.json << EOF
          {
            "AWSEBDockerrunVersion": "1",
            "Image": {
              "Name": "${{ steps.login-ecr.outputs.registry }}/${{ secrets.EB_APP_NAME }}:${{ github.sha }}",
              "Update": "true"
            },
            "Ports": [
              {
                "ContainerPort": 8000,
                "HostPort": 8000
              }
            ]
          }
          EOF

      - name: Generate .ebignore
        working-directory: vector3_ms/portfolio_manager
        run: |
          cat > .ebignore << EOF
          venv/
          __pycache__/
          *.pyc
          .env
          .git/
          EOF

      - name: Deploy to Elastic Beanstalk
        uses: einaregilsson/beanstalk-deploy@v22
        with:
          aws_access_key: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws_secret_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          region: ${{ secrets.AWS_REGION }}
          application_name: ${{ secrets.EB_APP_NAME }}
          environment_name: ${{ secrets.EB_ENV_NAME }}
          version_label: ${{ github.sha }}
          deployment_package: vector3_ms/portfolio_manager/Dockerrun.aws.json
          use_existing_version_if_exists: false

  # ─── FRONTEND: Build & Deploy to S3 + CloudFront ───
  deploy-frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: dashboard
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install deps & build
        run: |
          npm ci
          npm run build

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Sync to S3
        run: |
          aws s3 sync build/ s3://${{ secrets.S3_BUCKET }}/ --delete

      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CF_DISTRIBUTION_ID }} \
            --paths "/*"

  # ─── LAMBDA: Update daily ingestion function ───
  deploy-lambda:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: vector3_ms/lambda/daily_ingestion
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build & push Lambda image
        run: |
          IMAGE_TAG=${{ github.sha }}
          docker build -t ${{ secrets.LAMBDA_FUNCTION_NAME }}:$IMAGE_TAG .
          docker tag ${{ secrets.LAMBDA_FUNCTION_NAME }}:$IMAGE_TAG \
            ${{ steps.login-ecr.outputs.registry }}/${{ secrets.LAMBDA_FUNCTION_NAME }}:$IMAGE_TAG
          docker push ${{ steps.login-ecr.outputs.registry }}/${{ secrets.LAMBDA_FUNCTION_NAME }}:$IMAGE_TAG

      - name: Update Lambda function
        run: |
          aws lambda update-function-code \
            --function-name ${{ secrets.LAMBDA_FUNCTION_NAME }} \
            --image-uri ${{ steps.login-ecr.outputs.registry }}/${{ secrets.LAMBDA_FUNCTION_NAME }}:$IMAGE_TAG
```

---

## Phase 6: Environment Variable Management

### 6.1 EB Environment Variables

Set via `eb setenv` or AWS Console:
```
DB_HOST=<rds-endpoint>
DB_USER=admin
DB_PASS=<secure-password>
DB_NAME=portfolio_manager
JWT_SECRET=<random-64-char-string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ALPHA_VANTAGE_API_KEY=<key>
FINNHUB_API_KEY=<key>
```

### 6.2 Local `.env` File

**Never commit `.env` to git** (already in `.gitignore` ✅).

For local dev:
```
DB_HOST=localhost
DB_USER=root
DB_PASS=localpassword
DB_NAME=portfolio_manager
```

### 6.3 AWS Secrets Manager (Recommended)

```bash
aws secretsmanager create-secret \
  --name portfolio-manager/prod \
  --secret-string '{
    "DB_HOST":"...",
    "DB_USER":"...",
    "DB_PASS":"...",
    "JWT_SECRET":"..."
  }'
```

In Lambda and EB, retrieve secrets at runtime instead of env vars.

---

## Phase 7: Security Hardening

### 7.1 RDS Security
- [x] RDS in **private subnet** (no public access)
- [x] Security group allows 3306 **only from EB + Lambda SGs**
- [x] Encryption at rest enabled
- [x] Automated backups enabled

### 7.2 EB Security
- [x] ELB in **public subnets**, EC2 in **private subnets**
- [x] Health check URL configured
- [x] Rolling updates (zero-downtime)
- [x] Environment variables (not hardcoded)

### 7.3 S3 + CloudFront Security
- [x] S3 bucket policy: only CloudFront OAC can read
- [x] CloudFront: HTTPS required, TLS 1.2+
- [x] WAF rate limiting (optional)

### 7.4 Lambda Security
- [x] Lambda in VPC with NAT Gateway for internet
- [x] IAM role with least privilege
- [x] Environment variables encrypted at rest (KMS)

### 7.5 General
- [x] No secrets in code or Docker images
- [x] IAM users have MFA enabled
- [x] CloudTrail enabled for audit
- [x] S3 bucket versioning enabled

---

## Phase 8: Monitoring & Observability

### 8.1 CloudWatch
- **EB:** CPU, memory, request count, 5xx errors
- **RDS:** CPU, connections, disk space, replica lag
- **Lambda:** Invocations, duration, errors, throttles
- **CloudFront:** Requests, error rate, data transfer

### 8.2 Alarms

| Alarm | Metric | Threshold | Action |
|-------|--------|-----------|--------|
| High CPU | EB EC2 CPUUtilization | > 80% for 5 min | Scale up / SNS email |
| DB Connection Burst | RDS DatabaseConnections | > 80% of max | Scale up / SNS email |
| Lambda Error | Lambda Errors | > 0 for 1 min | SNS email |
| 5xx Spike | ELB 5xxCount | > 10 for 5 min | SNS email |

### 8.3 Logging

**Backend:** Already has `app/utils/logger.py` + `audit_service.py`. Logs go to CloudWatch automatically via EB.

**Lambda:** Logs go to CloudWatch Logs automatically.

**Dashboard:** (if using React) — `console.log` or Sentry for client-side errors.

---

## Phase 9: Cost Estimation (Monthly)

| Service | Config | Est. Cost |
|---------|--------|-----------|
| RDS | db.t3.micro (20GB) | ~$15 |
| Elastic Beanstalk | t3.small (1 instance) | ~$20 |
| S3 | 5GB + transfer | ~$1 |
| CloudFront | 50GB transfer | ~$5 |
| Lambda | 1M invocations/mo | ~$0 |
| NAT Gateway | 1 AZ | ~$32 |
| ECR | 2 images | ~$1 |
| **Total** | | **~$74/mo** |

**Cost savings:**
- Use t3.nano/micro for EB dev environment
- Remove NAT Gateway: use Lambda in public subnet (less secure)
- Use reserved instances for RDS (save ~40%)

---

## Phase 10: Production Launch Checklist

### Pre-Launch
- [ ] DNS propagated (Route 53)
- [ ] SSL certificates issued (ACM)
- [ ] CloudFront distribution deployed and active
- [ ] EB environment healthy, all endpoints respond
- [ ] RDS accessible from EB + Lambda only
- [ ] CORS configured for frontend domain
- [ ] JWT secret rotated
- [ ] API keys (Alpha Vantage, Finnhub) valid

### Post-Launch
- [ ] Lambda ingestion runs on schedule (check CloudWatch Logs)
- [ ] Frontend loads without errors
- [ ] API calls from frontend succeed
- [ ] CloudWatch alarms active
- [ ] Backups confirmed working
- [ ] CI/CD pipeline tested (push to main triggers deploy)

### Rollback Plan
- **EB:** `eb deploy --version <previous-version-label>`
- **S3:** `aws s3 sync s3://<bucket>/revisions/<prev-timestamp>/ s3://<bucket>/`
- **CloudFront:** Invalidate cache to serve old assets
- **Lambda:** `aws lambda update-function-code --function-name ... --image-uri <previous-image>`

---

## Files to Create Summary

| File | Location | Purpose |
|------|----------|---------|
| `Dockerfile` | `vector3_ms/portfolio_manager/` | Containerize FastAPI |
| `.dockerignore` | `vector3_ms/portfolio_manager/` | Exclude local artifacts |
| `Dockerrun.aws.json` | `vector3_ms/portfolio_manager/` | EB Docker config |
| `Procfile` | `vector3_ms/portfolio_manager/` | EB process declaration |
| `.ebignore` | `vector3_ms/portfolio_manager/` | EB zip exclusion |
| `lambda_function.py` | `vector3_ms/lambda/daily_ingestion/` | Lambda handler |
| `Dockerfile` | `vector3_ms/lambda/daily_ingestion/` | Lambda container image |
| `requirements.txt` | `vector3_ms/lambda/daily_ingestion/` | Lambda dependencies |
| `deploy.yml` | `.github/workflows/` | GitHub Actions CI/CD |

---

## Quick Reference Commands

```bash
# EB
eb init
eb create
eb deploy
eb setenv KEY=VALUE
eb open
eb logs

# S3
aws s3 sync build/ s3://<bucket>/ --delete

# CloudFront
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"

# Lambda
aws lambda invoke --function-name portfolio-daily-ingestion out.json
aws logs tail /aws/lambda/portfolio-daily-ingestion --follow

# RDS
aws rds describe-db-instances --db-instance-identifier portfolio-manager-db

# Docker
docker build -t portfolio-manager-api .
docker run -p 8000:8000 portfolio-manager-api
```
