import json
import uuid
from datetime import datetime

def process_bandit_findings(bandit_file):
    with open(bandit_file, 'r') as f:
        bandit_data = json.load(f)
    
    findings = []
    for result in bandit_data['results']:
        finding = {
            "SchemaVersion": "2018-10-08",
            "Id": str(uuid.uuid4()),
            "ProductArn": f"arn:aws:securityhub:{AWS_REGION}:{AWS_ACCOUNT_ID}:product/{AWS_ACCOUNT_ID}/default",
            "GeneratorId": "Bandit",
            "AwsAccountId": AWS_ACCOUNT_ID,
            "Types": ["Software and Configuration Checks/Vulnerabilities/CVE"],
            "CreatedAt": datetime.utcnow().isoformat() + "Z",
            "UpdatedAt": datetime.utcnow().isoformat() + "Z",
            "Severity": {
                "Label": result['issue_severity'].upper()
            },
            "Title": result['issue_text'],
            "Description": f"File: {result['filename']}, Line: {result['line_number']}",
            "Resources": [
                {
                    "Type": "Other",
                    "Id": result['filename']
                }
            ]
        }
        findings.append(finding)
    return findings

def process_dependency_check_findings(dc_file):
    with open(dc_file, 'r') as f:
        dc_data = json.load(f)
    
    findings = []
    for dependency in dc_data['dependencies']:
        if 'vulnerabilities' in dependency:
            for vuln in dependency['vulnerabilities']:
                finding = {
                    "SchemaVersion": "2018-10-08",
                    "Id": str(uuid.uuid4()),
                    "ProductArn": f"arn:aws:securityhub:{AWS_REGION}:{AWS_ACCOUNT_ID}:product/{AWS_ACCOUNT_ID}/default",
                    "GeneratorId": "OWASP Dependency-Check",
                    "AwsAccountId": AWS_ACCOUNT_ID,
                    "Types": ["Software and Configuration Checks/Vulnerabilities/CVE"],
                    "CreatedAt": datetime.utcnow().isoformat() + "Z",
                    "UpdatedAt": datetime.utcnow().isoformat() + "Z",
                    "Severity": {
                        "Label": vuln['severity'].upper()
                    },
                    "Title": vuln['name'],
                    "Description": vuln['description'],
                    "Resources": [
                        {
                            "Type": "Other",
                            "Id": dependency['fileName']
                        }
                    ]
                }
                findings.append(finding)
    return findings

if __name__ == "__main__":
    AWS_REGION = "us-east-1"  # Replace with your AWS region
    AWS_ACCOUNT_ID = "921300860955"  # Replace with your AWS account ID

    bandit_findings = process_bandit_findings('bandit-results.json')
    dc_findings = process_dependency_check_findings('./reports/dependency-check-report.json')
    
    all_findings = bandit_findings + dc_findings
    
    with open('security-hub-findings.json', 'w') as f:
        json.dump(all_findings, f)
