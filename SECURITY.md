# Security Guidelines for Cardano NFT Vending Machine

## ⚠️ CRITICAL SECURITY NOTICE

This software handles **REAL CURRENCY** (ADA/Lovelace) on the Cardano blockchain. Security failures can result in **permanent financial loss**. Follow these guidelines without exception.

## Table of Contents

- [Key Management](#key-management)
- [Server Access & Network Security](#server-access--network-security)
- [Operational Best Practices](#operational-best-practices)
- [Monitoring & Incident Response](#monitoring--incident-response)
- [Cardano Security Resources](#cardano-security-resources)

## Key Management

### 🔑 Never Share or Expose Private Keys

**Private keys (`.skey` files) are the most critical security asset. Treat them as highly sensitive.**

#### Do:
- ✅ Store signing keys on an isolated server with minimal attack surface
- ✅ Use hardware wallets (Ledger/Trezor) for profit addresses
- ✅ Encrypt keys at rest using filesystem encryption (LUKS, BitLocker)
- ✅ Use strong passwords (20+ characters, random) if protecting keys with passwords
- ✅ Create separate keys for each role (payment vs profit vs minting)
- ✅ Use read-only access for service accounts that only read keys
- ✅ Implement key rotation procedures for periodic re-keying
- ✅ Backup keys to secure, encrypted offline storage

#### Don't:
- ❌ **NEVER** commit keys to version control
- ❌ **NEVER** share keys over insecure channels
- ❌ **NEVER** store keys in publicly accessible directories
- ❌ **NEVER** transmit keys over email, Slack, or other communication tools
- ❌ **NEVER** use the same key across multiple environments
- ❌ **NEVER** keep keys on shared or public servers
- ❌ **NEVER** log keys or key material

### Recommended Key Storage Architecture

```
Production Environment:
├── payment.skey         (Minimal permissions, isolated storage)
├── mint.skey           (Backup stored offline, encrypted)
└── [profit_address]    (HARDWARE WALLET - Ledger/Trezor)

Development/Test:
├── test-keys/          (Separate testnet keys, clearly labeled)
└── NOT in production
```

## Server Access & Network Security

### Server Hardening

#### SSH Security

**Implement SSH key-based authentication and disable password logins:**

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
Port 22  # Consider changing to non-standard port
MaxAuthTries 3
```

#### IP Whitelisting with iptables

**Only allow access from trusted IPs:**

```bash
# Allow only specific IPs for SSH
iptables -A INPUT -p tcp -s TRUSTED_IP_1 --dport 22 -j ACCEPT
iptables -A INPUT -p tcp -s TRUSTED_IP_2 --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP

# Allow only specific IPs for vending machine (if accessible)
# WARNING: Only expose if absolutely necessary with full auth
```

#### Firewall Configuration

**Block all unnecessary ports and services:**

```bash
# Flush existing rules
iptables -F
iptables -X

# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow specific IPs for SSH
iptables -A INPUT -p tcp -s YOUR_IP --dport 22 -j ACCEPT

# Block everything else
iptables -A INPUT -j DROP
```

See [iptables documentation](https://www.cyberciti.biz/tips/linux-iptables-4-block-all-incoming-traffic-but-allow-ssh.html) for detailed configuration.

### Network Isolation

**Consider network-level protections:**

- Use a private subnet for the vending machine server
- Deploy a VPN for secure remote access
- Implement VPC security groups (AWS) or equivalent in your cloud provider
- Use a dedicated firewall appliance for enterprise environments

## Operational Best Practices

### Pre-Production Checklist

Before running on mainnet:

- [ ] All keys stored securely and backed up
- [ ] Profit address uses hardware wallet (Ledger/Trezor)
- [ ] Server hardened with SSH keys, IP whitelisting, firewall
- [ ] All software dependencies updated (`pip list --outdated`)
- [ ] Thorough testing on testnet (preprod or preview)
- [ ] Protocol parameters validated
- [ ] Metadata and scripts verified
- [ ] Monitoring and alerts configured
- [ ] Incident response plan documented
- [ ] Team members trained on procedures
- [ ] Access logs enabled and monitored

### Running the Vending Machine

#### Configuration Security

**Validate all configuration before starting:**

```bash
# Always validate before running
python3 main.py validate \
  --payment-addr <ADDR> \
  --payment-sign-key /secure/path/to/payment.skey \
  --profit-addr <ADDR> \
  --mint-price <PRICE> LOVELACE \
  --mint-script /path/to/policy.script \
  --mint-sign-key /secure/path/to/mint.skey \
  --blockfrost-project <PROJECT_ID> \
  --metadata-dir metadata/ \
  --output-dir output/ \
  --single-vend-max <MAX> \
  --no-whitelist \
  --mainnet
```

#### Service Account Permissions

**Use least-privilege principles:**

```bash
# Create dedicated service account
useradd -m -s /bin/bash vending-machine

# Give read-only access to keys
chmod 600 /secure/path/to/*.skey
chown root:vending-machine /secure/path/to/payment.skey
chmod 640 /secure/path/to/payment.skey

# Give write access to output directory
chown -R vending-machine:vending-machine /path/to/output
```

#### Process Management

**Run as a service with proper logging:**

```bash
# systemd service example: /etc/systemd/system/vending-machine.service
[Unit]
Description=Cardano NFT Vending Machine
After=network.target

[Service]
Type=simple
User=vending-machine
WorkingDirectory=/opt/vending-machine
ExecStart=/usr/bin/python3 /opt/vending-machine/main.py run [args]
Restart=always
RestartSec=10
StandardOutput=append:/var/log/vending-machine/output.log
StandardError=append:/var/log/vending-machine/error.log

[Install]
WantedBy=multi-user.target

# Enable and start
systemctl enable vending-machine
systemctl start vending-machine
```

### Access Control

#### Principle of Least Privilege

- Only grant access to essential personnel
- Use separate accounts for operators
- Implement role-based access control (RBAC) if possible
- Review access logs regularly

#### SSH Key Management

```bash
# Generate strong SSH keys
ssh-keygen -t ed25519 -a 256 -f ~/.ssh/vending_machine_key

# Authorize only specific keys
cat authorized_keys  # Review carefully before adding
```

## Monitoring & Incident Response

### Monitoring Setup

**Monitor critical system metrics:**

```bash
# Disk space
df -h /path/to/output /path/to/metadata

# Process health
systemctl status vending-machine

# Network activity
netstat -tuln | grep 22

# Failed login attempts
grep "Failed password" /var/log/auth.log
```

### Logging

**Enable comprehensive logging:**

```python
# Example: Add to your vending machine script
import logging

logging.basicConfig(
    filename='/var/log/vending-machine/transactions.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Incident Response Plan

**If you suspect a security breach:**

1. **IMMEDIATELY** disconnect the server from the network
2. Stop the vending machine process
3. Assess damage: Check transaction history and logs
4. Rotate all keys (if compromise confirmed)
5. Contact relevant parties:
   - Cardano development team
   - Your security team
   - Legal/compliance (if applicable)
6. Document everything
7. Restore from secure backups if necessary

**Never restart the vending machine without understanding the incident.**

### Backup and Recovery

#### Key Backups

```bash
# Create encrypted backup
tar -czf keys-backup.tar.gz /path/to/keys/
gpg --symmetric --cipher-algo AES256 keys-backup.tar.gz
# Store encrypted backup offline
```

#### Metadata and Configuration Backups

```bash
# Backup metadata
rsync -av metadata/ /secure/backup/location/metadata/

# Backup configuration
tar -czf vm-config-$(date +%Y%m%d).tar.gz config/ scripts/
```

## Cardano Security Resources

### Official Documentation

- [Cardano Security Best Practices](https://docs.cardano.org/cardano-testnet/getting-started/security-best-practices)
- [Cardano Security Architecture](https://docs.cardano.org/core-concepts/security-architecture)
- [Hardware Wallet Guide](https://www.ledger.com/blog/what-is-cardano-ada)

### Community Resources

- [Cardano Security Reddit](https://www.reddit.com/r/cardano)
- [Cardano Developer Portal](https://developers.cardano.org)
- [Input Output Global Security Advisories](https://iohk.io/cn/blog)

### Additional Reading

- [Linux Server Hardening Guide](https://www.cyberciti.biz/tips/linux-security.html)
- [iptables Configuration Guide](https://www.cyberciti.biz/tips/linux-iptables-4-block-all-incoming-traffic-but-allow-ssh.html)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Security Audit Checklist

Before going live on mainnet, complete this audit:

### Infrastructure
- [ ] Server patched with latest security updates
- [ ] Unnecessary services disabled
- [ ] Firewall configured and tested
- [ ] IP whitelisting implemented
- [ ] SSH key-based authentication only
- [ ] Automated backups configured
- [ ] Monitoring and alerting active

### Keys & Credentials
- [ ] Profit address uses hardware wallet
- [ ] All `.skey` files encrypted at rest
- [ ] Backup keys stored offline and encrypted
- [ ] No keys in version control (check `.gitignore`)
- [ ] Blockfrost API keys secured
- [ ] Key rotation plan documented

### Application
- [ ] Thoroughly tested on testnet
- [ ] All dependencies up to date
- [ ] Configuration validated
- [ ] Metadata verified
- [ ] Scripts validated
- [ ] Error handling tested

### Personnel
- [ ] Access control reviewed
- [ ] Team trained on procedures
- [ ] Incident response plan documented
- [ ] Emergency contacts listed
- [ ] Security awareness training completed

## Reporting Security Issues

If you discover a security vulnerability in this software:

1. **DO NOT** create a public GitHub issue
2. Email security@project-maintainer.tld (replace with actual address)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Your contact information

We take security seriously and will respond promptly.

## Disclaimer

**NO WARRANTIES**: This software is provided "as is" without any warranties. By using this software, you acknowledge that:

- You are responsible for your own security
- There are NO WARRANTIES regarding the safety of funds
- You use this software at your own risk
- Loss of funds due to security issues is your responsibility
- Always conduct independent security audits

**USE AT YOUR OWN RISK.**
