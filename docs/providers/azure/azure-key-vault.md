# Azure Key Vault

Source pages:
- Azure Key Vault Overview: https://learn.microsoft.com/en-us/azure/key-vault/general/overview
- Secure your Azure Key Vault: https://learn.microsoft.com/en-us/azure/key-vault/general/security-features

## Azure Key Vault Overview

Source: https://learn.microsoft.com/en-us/azure/key-vault/general/overview

# About Azure Key Vault

Azure Key Vault is one of several key management solutions in Azure (/en-us/azure/security/fundamentals/key-management) , and helps solve the following problems:

- Secrets Management - Azure Key Vault can be used to Securely store and tightly control access to tokens, passwords, certificates, API keys, and other secrets
- Key Management - Azure Key Vault can be used as a Key Management solution. Azure Key Vault makes it easy to create and control the encryption keys used to encrypt your data.
- Certificate Management - Azure Key Vault lets you easily provision, manage, and deploy public and private Transport Layer Security/Secure Sockets Layer (TLS/SSL) certificates for use with Azure and your internal connected resources.

Azure Key Vault offers two service tiers to meet different security and compliance requirements:

- Standard tier - Encrypts data using software libraries validated to FIPS 140 Level 1
- Premium tier - Offers HSM-protected keys, generated and protected by FIPS 140-3 Level 3 validated Marvell LiquidSecurity HSMs, for the highest level of cryptographic protection

For detailed pricing and feature comparisons between tiers, see the Azure Key Vault pricing page (https://azure.microsoft.com/pricing/details/key-vault/) .

Zero Trust (/en-us/security/zero-trust/zero-trust-overview) is a security strategy comprising three principles: "Verify explicitly", "Use least privilege access", and "Assume breach". Data protection, including key management, supports the "use least privilege access" principle. For more information, see What is Zero Trust? (/en-us/security/zero-trust/zero-trust-overview)

## Why use Azure Key Vault?

### Centralize application secrets

Centralizing storage of application secrets in Azure Key Vault allows you to control their distribution. Key Vault greatly reduces the chances that secrets may be accidentally leaked. When application developers use Key Vault, they no longer need to store security information in their application. Not having to store security information in applications eliminates the need to make this information part of the code. For example, an application may need to connect to a database. Instead of storing the connection string in the app's code, you can store it securely in Key Vault.

Your applications can securely access the information they need by using URIs. These URIs allow the applications to retrieve specific versions of a secret. There's no need to write custom code to protect any of the secret information stored in Key Vault.

### Securely store secrets and keys

Access to a key vault requires proper authentication and authorization before a caller (user or application) can get access. Authentication establishes the identity of the caller, while authorization determines the operations that they're allowed to perform.

Authentication is done via Microsoft Entra ID. Authorization may be done via Azure role-based access control (Azure RBAC) or Key Vault access policy. Azure RBAC can be used for both management of the vaults and to access data stored in a vault, while key vault access policy can only be used when attempting to access data stored in a vault.

Azure Key Vault provides multiple layers of security to protect your data. All key vaults are encrypted at rest using keys stored in hardware security modules (HSMs), and Azure safeguards your keys, secrets, and certificates using industry-standard algorithms, key lengths, and cryptographic protection.

For organizations requiring the highest level of security, the Premium tier offers HSM-protected keys (RSA-HSM, EC-HSM, or OCT-HSM) that never leave the HSM boundary. These Premium tier HSMs utilize Marvell LiquidSecurity hardware with FIPS 140-3 Level 3 validation, ensuring the most stringent cryptographic protection available.

Both Standard and Premium tiers use Federal Information Processing Standard 140 validated software cryptographic modules and HSMs (/en-us/azure/key-vault/keys/about-keys#compliance) to meet rigorous security and compliance standards.

Finally, Azure Key Vault is designed so that Microsoft doesn't see or extract your data.

### Monitor access and use

Once you've created a couple of Key Vaults, you'll want to monitor how and when your keys and secrets are being accessed. You can monitor activity by enabling logging for your vaults. You can configure Azure Key Vault to:

- Archive to a storage account.
- Stream to an event hub.
- Send the logs to Azure Monitor logs.

You have control over your logs and you may secure them by restricting access and you may also delete logs that you no longer need.

### Simplified administration of application secrets

When storing valuable data, you must take several steps. Security information must be secured, it must follow a life cycle, and it must be highly available. Azure Key Vault simplifies the process of meeting these requirements by:

- Removing the need for in-house knowledge of Hardware Security Modules.
- Scaling up on short notice to meet your organization's usage spikes.
- Replicating the contents of your Key Vault within a region and to a secondary region. Data replication ensures high availability and takes away the need of any action from the administrator to trigger the failover.
- Providing standard Azure administration options via the portal, Azure CLI and PowerShell.
- Automating certain tasks on certificates that you purchase from Public CAs, such as enrollment and renewal.

In addition, Azure Key Vaults allow you to segregate application secrets. Applications may access only the vault that they're allowed to access, and they can be limited to only perform specific operations. You can create an Azure Key Vault per application and restrict the secrets stored in a Key Vault to a specific application and team of developers.

### Integrate with other Azure services

As a secure store in Azure, Key Vault has been used to simplify scenarios like:

- Azure Disk Encryption (/en-us/azure/security/fundamentals/encryption-overview)
- The always encrypted (/en-us/sql/relational-databases/security/encryption/always-encrypted-database-engine) and Transparent Data Encryption (/en-us/sql/relational-databases/security/encryption/transparent-data-encryption) functionality in SQL server and Azure SQL Database
- Azure App Service (/en-us/azure/app-service/configure-ssl-certificate) .

Key Vault itself can integrate with storage accounts, event hubs, and log analytics.

## Next steps

- Key management in Azure (/en-us/azure/security/fundamentals/key-management)
- Learn more about keys, secrets, and certificates (about-keys-secrets-certificates)
- Quickstart: Create an Azure Key Vault using the CLI (../secrets/quick-create-cli)
- Authentication, requests, and responses (authentication-requests-and-responses)
- What is Zero Trust? (/en-us/security/zero-trust/zero-trust-overview)

## Feedback

Was this page helpful?

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

## Additional resources

- Last updated on 2025-12-03


## Secure your Azure Key Vault

Source: https://learn.microsoft.com/en-us/azure/key-vault/general/security-features

# Secure your Azure Key Vault

Azure Key Vault protects cryptographic keys, certificates (and the private keys associated with the certificates), and secrets (such as connection strings and passwords) in the cloud. When storing sensitive and business-critical data, however, you must take steps to maximize the security of your vaults and the data stored in them.

The security recommendations in this article implement Zero Trust principles: "Verify explicitly", "Use least privilege access", and "Assume breach". For comprehensive Zero Trust guidance, see the Zero Trust Guidance Center (/en-us/security/zero-trust/) .

This article provides security recommendations to help protect your Azure Key Vault deployment.

## Service-specific security

Azure Key Vault has unique security considerations related to vault architecture and appropriate use of the service for storing cryptographic materials.

### Key vault architecture

Use one Key Vault per application, region, and environment : Create separate Key Vaults for development, preproduction, and production environments to reduce the impact of breaches.

Key vaults define security boundaries for stored secrets. Grouping secrets into the same vault increases the blast radius of a security event because attacks might be able to access secrets across concerns. To mitigate access across concerns, consider what secrets a specific application should have access to, and then separate your key vaults based on this delineation. Separating key vaults by application is the most common boundary. Security boundaries, however, can be more granular for large applications, for example, per group of related services.

Use one Key Vault per tenant in multitenant solutions : For multitenant SaaS solutions, use a separate Key Vault for each tenant to maintain data isolation. This is the recommended approach for secure isolation of customer data and workloads. See Multitenancy and Azure Key Vault (/en-us/azure/architecture/guide/multitenant/service/key-vault) .

### Object Storage in Key Vault

Do not use Key Vault as a data storage to store customer configurations or service configurations : Services should use Azure Storage with encryption at rest (/en-us/azure/storage/common/storage-service-encryption) or Azure configuration manager (/en-us/mem/configmgr/core/understand/introduction) . Storage is more performant for such scenarios.

Do not store certificates (customer or service owned) as secrets : Service-owned certificates should be stored as Key Vault certificates and configured for autorotation. For more information, see Azure key vault: Certificates (../certificates/about-certificates) and Understanding autorotation in Azure Key Vault .

- Customer content (excluding secrets and certificates) should not be stored in Key Vault : Key Vault is not a data store and not built to scale like a data store. Instead use a proper data store like Cosmos DB (/en-us/azure/cosmos-db/introduction) or Azure Storage (/en-us/azure/storage/common/storage-introduction) . Customers have the option of BYOK (Bring Your Own Key) for encryption at rest. This key can be stored in Azure Key Vault to encrypt the data in Azure Storage.

## Network Security

Reducing network exposure is critical to protecting Azure Key Vault from unauthorized access. Configure network restrictions based on your organization's requirements and use case. For detailed information and step-by-step configuration instructions, see Configure network security for Azure Key Vault (network-security) .

These network security features are listed from most restricted to least restricted capabilities. Pick the configuration that best suits your organization's use case.

Disable public network access and use Private Endpoints only : Deploy Azure Private Link to establish a private access point from a virtual network to Azure Key Vault and prevent exposure to the public internet. For implementation steps, see Integrate Key Vault with Azure Private Link (private-link-service) .

- Some customer scenarios require trusted Microsoft services to bypass the firewall, in such cases the vault might need to be configured to allow Trusted Microsoft Services. For full details, see Configure network security: Key Vault Firewall Enabled (Trusted Services Only) (network-security#key-vault-firewall-enabled-trusted-services-only) .

Enable Key Vault Firewall : Limit access to public static IP addresses or your virtual networks. For full details, see Configure network security: Firewall settings (network-security#firewall-settings) .

- Some customer scenarios require trusted Microsoft services to bypass the firewall, in such cases the vault might need to be configured to allow Trusted Microsoft Services.

Use Network Security Perimeter : Define a logical network isolation boundary for PaaS resources (for example, Azure Key Vault, Azure Storage and SQL Database) that are deployed outside your organization's virtual network perimeter and/or public static IP addresses. For full details, see Configure network security: Network Security Perimeter (network-security#network-security-perimeter) .

- `publicNetworkAccess: SecuredByPerimeter`overrides "Allow trusted Microsoft services to bypass the firewall", meaning that some scenarios that require that trust will not work.

## TLS and HTTPS

Azure Key Vault supports TLS 1.2 and 1.3 protocol versions to ensure secure communication between clients and the service.

- Enforce TLS version control : The Key Vault front end (data plane) is a multitenant server where key vaults from different customers can share the same public IP address. To achieve isolation, each HTTP request is authenticated and authorized independently. The HTTPS protocol allows clients to participate in TLS negotiation, and clients can enforce the TLS version to ensure the entire connection uses the corresponding level of protection. See Key Vault logging for sample Kusto queries to monitor TLS versions used by clients.

## Identity and access management

Azure Key Vault uses Microsoft Entra ID for authentication. Access is controlled through two interfaces: the control plane (for managing Key Vault itself) and the data plane (for working with keys, secrets, and certificates). For details on the access model and endpoints, see Azure RBAC for Key Vault data plane operations (rbac-guide) .

Enable managed identities : Use Azure managed identities for all app and service connections to Azure Key Vault to eliminate hard-coded credentials. Managed identities help secure authentication while removing the need for explicit credentials. For authentication methods and scenarios, see Azure Key Vault authentication .

Use role-based access control : Use Azure Role-Based Access Control (RBAC) to manage access to the Azure Key Vault. For more information, see Azure RBAC for Key Vault data plane operations (rbac-guide) .

- Do not use legacy access policies : Legacy access policies have known security vulnerabilities and lack support for Privileged Identity Management (PIM), and should not be used for critical data and workloads. Azure RBAC mitigates potential unauthorized Key Vault access risks. See Azure role-based access control (Azure RBAC) vs. access policies (legacy) (rbac-access-policy) .

Important

RBAC permission model allows vault-level role assignments for persistent access and eligible (JIT) assignments for privileged operations. Object-scope assignments only support read operations; administrative operations like network access control, monitoring, and object management require vault-level permissions. For secure isolation across application teams, use one Key Vault per application.

Assign just-in-time (JIT) privileged roles : Use Azure Privileged Identity Management (PIM) to assign eligible JIT Azure RBAC roles for administrators and operators of Key Vault. See Privileged Identity Management (PIM) overview (/en-us/entra/id-governance/privileged-identity-management/pim-configure) for details.

- Require approvals for privileged role activation : Add an extra layer of security to prevent unauthorized access by ensuring that at least one approver is required to activate JIT roles. See Configure Microsoft Entra role settings in Privileged Identity Management (/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings) .
- Enforce multi-factor authentication for role activation : Require MFA to activate JIT roles for operators and administrators. See Microsoft Entra multifactor authentication (/en-us/entra/identity/authentication/concept-mfa-howitworks) .

Enable Microsoft Entra Conditional Access Policies : Key Vault supports Microsoft Entra Conditional Access policies to apply access controls based on conditions such as user location or device. For more information, see Conditional Access overview (/en-us/entra/identity/conditional-access/overview) .

Apply the principle of least privilege : Limit the number of users with administrative roles and ensure users are granted only the minimum permissions required for their role. See Enhance security with the principle of least privilege (/en-us/entra/identity-platform/secure-least-privileged-access)

## Data Protection

Protecting data stored in Azure Key Vault requires enabling soft delete, purge protection, and implementing automated rotation of cryptographic materials.

Turn on soft delete : Ensure that soft delete is enabled so that deleted Key Vault objects can be recovered within a 7 to 90-day retention period. See Azure Key Vault soft-delete overview (soft-delete-overview) .

Turn on purge protection : Enable purge protection to protect against accidental or malicious deletion of Key Vault objects even after soft delete is enabled. See Azure Key Vault soft-delete overview: Purge Protection (soft-delete-overview#purge-protection)

Implement autorotation for cryptographic assets : Configure automatic rotation of keys, secrets, and certificates to minimize the risk of compromise and ensure compliance with security policies. Regular rotation of cryptographic materials is a critical security practice. See Understanding autorotation in Azure Key Vault , Configure key autorotation (../keys/how-to-configure-key-rotation) , Configure certificate autorotation (../certificates/tutorial-rotate-certificates) , Automate secret rotation for resources with one set of authentication credentials (../secrets/tutorial-rotation) , and Automate secret rotation for resources with two sets of authentication credentials (../secrets/tutorial-rotation-dual) .

## Compliance and governance

Regular compliance audits and governance policies ensure your Key Vault deployment adheres to security standards and organizational requirements.

- Use Azure Policy to enforce configuration : Configure Azure Policy to audit and enforce secure configurations for Azure Key Vault and set up alerts for deviations from policy. See Azure Policy Regulatory Compliance controls for Azure Key Vault (../security-controls-policy) .

## Logging and Threat Detection

Comprehensive logging and monitoring enable detection of suspicious activities and compliance with audit requirements.

Enable audit logging : Key Vault logging saves information about operations performed on the vault. For full details, see Key Vault logging .

Enable Microsoft Defender for Key Vault : Enable Microsoft Defender for Key Vault to monitor for and alert on suspicious activity. For details, see Microsoft Defender for Key Vault introduction (/en-us/azure/defender-for-cloud/defender-for-key-vault-introduction) .

Enable log alerts for security events : Set up alerts to be notified when critical events are logged, such as access failures or secret deletions. See Monitoring and alerting for Azure Key Vault .

Monitor and alert : Integrate Key Vault with Event Grid to receive notifications on changes to keys, certificates, or secrets. For details, see Monitoring Key Vault with Azure Event Grid (event-grid-overview) .

## Backup and Recovery

Regular backups ensure business continuity and protect against data loss from accidental or malicious deletion.

Enable native backup for Azure Key Vault : Configure and use the Azure Key Vault native backup feature to back up secrets, keys, and certificates, ensuring recoverability. See Azure Key Vault backup .

Ensure backups for secrets that can't be recreated : Back up Key Vault objects (like encryption keys) that can't be recreated from other sources. See Azure Key Vault backup .

Test backup and recovery procedures : To verify the effectiveness of backup processes, regularly test the restoration of Key Vault secrets, keys, and certificates. See Azure Key Vault backup .

## Related security articles

For security best practices specific to keys, secrets, and certificates, see:

- Secure your Azure Key Vault keys (../keys/secure-keys) - Key-specific security best practices including rotation, HSM protection, and BYOK
- Secure your Azure Key Vault secrets (../secrets/secure-secrets) - Secrets-specific security best practices including rotation, caching, and monitoring
- Secure your Azure Key Vault certificates (../certificates/secure-certificates) - Certificate-specific security best practices including lifecycle management, renewal, and CA integration

## Next steps

- Azure Key Vault security baseline (/en-us/security/benchmark/azure/baselines/key-vault-security-baseline)
- Secure your Azure Managed HSM deployment (../managed-hsm/secure-managed-hsm)
- Virtual network service endpoints for Azure Key Vault (overview-vnet-service-endpoints)
- Azure RBAC: Built-in roles (/en-us/azure/role-based-access-control/built-in-roles)

## Feedback

Was this page helpful?

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

## Additional resources

- Last updated on 2026-01-30
