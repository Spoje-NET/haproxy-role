#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import os
import configparser
import subprocess
from datetime import datetime

RENEWAL_DIR = '/etc/letsencrypt/renewal/'

DOCUMENTATION = r'''
---
module: certbot_certificates

short_description: Gathers information about Certbot-managed certificates.

version_added: "1.0.0"

description: >
    This module reads renewal configuration files from /etc/letsencrypt/renewal/
    and returns metadata about each certificate, including name, path, expiry date,
    and days until expiration.

author:
    - Vítězslav Dvořák (@Vitexus)

options: {}

requirements:
  - The renewal directory (/etc/letsencrypt/renewal/) must exist
  - Certificates must be managed by Certbot

'''

EXAMPLES = r'''
# Get list of all certificates managed by Certbot
- name: Get certbot certificates
  certbot_certificates:
  register: certs_info

- name: Show certificate info
  debug:
    var: certs_info.certificates
'''

RETURN = r'''
certificates:
  description: List of certificates found in /etc/letsencrypt/renewal/
  type: list
  returned: always
  elements: dict
  sample:
    - name: example.com
      cert_path: /etc/letsencrypt/live/example.com/cert.pem
      expiry_date: "2025-06-10 12:00:00"
      days_until_expiration: 30
'''

def get_cert_expiry(cert_path):
    """
    Parses the certificate at cert_path using OpenSSL to extract the expiration date.
    Returns a datetime object or None if parsing fails.
    """
    try:
        result = subprocess.run(
            ["openssl", "x509", "-noout", "-enddate", "-in", cert_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        # Example output: notAfter=Jun 10 12:00:00 2025 GMT
        line = result.stdout.strip()
        if line.startswith("notAfter="):
            expiry_str = line.split("=", 1)[1].strip()
            expiry_date = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
            return expiry_date
    except Exception:
        return None


def parse_renewal_files():
    certificates = []

    if not os.path.isdir(RENEWAL_DIR):
        return {"failed": True, "msg": f"Renewal directory not found: {RENEWAL_DIR}"}

    for filename in os.listdir(RENEWAL_DIR):
        if filename.endswith(".conf"):
            filepath = os.path.join(RENEWAL_DIR, filename)
            config = configparser.ConfigParser()
            try:
                with open(filepath, 'r') as f:
                    content = f.read()

                # Add [default] section header if missing
                if not content.strip().startswith('['):
                    content = '[default]\n' + content

                config.read_string(content)

                cert_name = filename.replace(".conf", "")
                cert_path = config.get('default', 'cert', fallback=None)
                fullchain_path = config.get('default', 'fullchain', fallback=None)

                expiry_date = get_cert_expiry(fullchain_path)
                if expiry_date:
                    days_until_expiration = (expiry_date - datetime.now()).days
                    expiry_str = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    expiry_str = "unknown"
                    days_until_expiration = -1

                certificates.append({
                    "name": cert_name,
                    "cert_path": cert_path,
                    "fullchain_path": fullchain_path,
                    "expiry_date": expiry_str,
                    "days_until_expiration": days_until_expiration
                })
            except Exception as e:
                return {"failed": True, "msg": f"Failed to parse {filename}: {str(e)}"}

    return {"failed": False, "certificates": certificates}

def main():
    module = AnsibleModule(
        argument_spec={},
        supports_check_mode=True
    )

    result = parse_renewal_files()
    if result["failed"]:
        module.fail_json(msg=result["msg"])
    else:
        module.exit_json(changed=False, certificates=result["certificates"])

if __name__ == "__main__":
    main()
