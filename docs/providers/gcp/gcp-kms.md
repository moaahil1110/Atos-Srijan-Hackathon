# GCP Cloud KMS

Source pages:
- Cloud Key Management Service overview: https://cloud.google.com/kms/docs/concepts
- Key rotation: https://cloud.google.com/kms/docs/key-rotation

## Cloud Key Management Service overview

Source: https://cloud.google.com/kms/docs/concepts

# Cloud Key Management Service overview

Cloud Key Management Service (Cloud KMS) lets you create and manage cryptographic keys for use in compatible Google Cloud services and in your own applications. Using Cloud KMS, you can do the following:

- Generate software or hardware keys, import existing keys into Cloud KMS, or link external keys in your compatible external key management (EKM) system (/kms/docs/ekm#supported_partners) .
- Generate Multi-tenant Cloud HSM keys and use them with Cloud HSM for Google Workspace (/kms/docs/onboard-hsm-workspace) to enable client-side encryption (CSE) in Google Workspace.
- Create and maintain Single-tenant Cloud HSM (/kms/docs/single-tenant-hsm) instances, and create or import and then use Single-tenant Cloud HSM keys.
- Use customer-managed encryption keys (CMEKs) in Google Cloud products with CMEK integration (/kms/docs/cmek) . CMEK integrations use your Cloud KMS keys to encrypt or "wrap" your data encryption keys (DEKs). Wrapping DEKs with key encryption keys (KEKs) is called envelope encryption (/kms/docs/envelope-encryption) .
- Use Cloud KMS Autokey (/kms/docs/autokey-overview) to automate provisioning and assignment. With Autokey, you don't need to provision key rings, keys, and service accounts ahead of time. Instead, they are generated on demand as part of resource creation.
- Use Cloud KMS keys for encryption and decryption operations. For example, you can use the Cloud KMS API or client libraries to use your Cloud KMS keys for client-side encryption (/kms/docs/client-side-encryption) .
- Use Cloud KMS keys to create or verify digital signatures (/kms/docs/digital-signatures) or message authentication code (MAC) signatures (/kms/docs/mac-signatures) .
- Use Cloud KMS keys to establish shared secrets using key encapsulation mechanisms (/kms/docs/key-encapsulation-mechanisms) .

## Choose the right encryption for your needs

You can use the following table to identify which type of encryption meets your needs for each use case. The best solution for your needs might include a mix of encryption approaches. For example, you might use software keys for your least sensitive data and hardware or external keys for your most sensitive data. For additional information about the encryption options described in this section, see Protecting data in Google Cloud (#protecting-data) on this page. For more information about the service level agreement (SLA) that applies when using Cloud KMS, Cloud HSM, and Cloud EKM keys, see Service Level Agreement (/kms/sla) .

Encryption type Cost Compatible services Features

Google-owned and Google-managed encryption keys (Google Cloud default encryption) (/docs/security/encryption/default-encryption#googles_default_encryption) Included All Google Cloud services that store customer data

- No configuration required.
- Automatically encrypts customer data saved in any Google Cloud service.
- Most services automatically rotate keys.
- Supports encryption using AES-256.
- FIPS 140-2 Level 1 validated.

Customer-managed encryption keys (/kms/docs/protection-levels#software) - software
(Cloud KMS keys) $0.06 per key version 40+ services (/kms/docs/compatible-services)

- You control automatic key rotation schedule; IAM roles and permissions; enable, disable, or destroy key versions.
- Supports symmetric and asymmetric keys for encryption and decryption (/kms/docs/algorithms#key_purposes) .
- Automatically rotates symmetric keys (/kms/docs/key-rotation) .
- Supports several common algorithms (/kms/docs/algorithms) .
- FIPS 140-2 Level 1 validated.
- Keys are unique to a customer.

Customer-managed encryption keys - hardware (/kms/docs/protection-levels#hardware)
(Cloud HSM keys) $1.00 to $2.50 per key version per month 40+ services (/kms/docs/compatible-services)

- Optionally managed through Cloud KMS Autokey.
- You control automatic key rotation schedule; IAM roles and permissions; enable, disable, or destroy key versions.
- Supports symmetric and asymmetric keys for encryption and decryption (/kms/docs/algorithms#key_purposes) .
- Automatically rotates symmetric keys (/kms/docs/key-rotation) .
- Supports several common algorithms (/kms/docs/algorithms) .
- FIPS 140-2 Level 3 validated.
- Keys are unique to a customer.
- You can create and manage your own Single-tenant Cloud HSM instance to have more cryptographic isolation and greater administrative control of your HSM keys. Single-tenant Cloud HSM instances incur additional costs.

Customer-managed encryption keys - external (/kms/docs/protection-levels#external)
(Cloud EKM keys) $3.00 per key version per month 30+ services (/kms/docs/compatible-services#ekm)

- You control IAM roles and permissions; enable, disable, or destroy key versions.
- Keys are never sent to Google.
- Key material resides in a compatible external key management (EKM) provider (/kms/docs/ekm#supported_partners) .
- Compatible Google Cloud services connect to your EKM provider over the internet (/kms/docs/ekm#ekm-internet) or a Virtual Private Cloud (VPC) (/kms/docs/ekm#ekm-vpc) .
- Supports symmetric keys for encryption and decryption (/kms/docs/algorithms#key_purposes) .
- Manually rotate your keys in coordination with Cloud EKM and your EKM provider.
- FIPS 140-2 Level 2 or FIPS 140-2 Level 3 validated, depending on the EKM.
- Keys are unique to a customer.

Client-side encryption using Cloud KMS keys (/kms/docs/client-side-encryption) Cost of active key versions depends on the protection level of the key. Use client libraries (/kms/docs/reference/libraries) in your applications

- You control automatic key rotation schedule; IAM roles and permissions; enable, disable, or destroy key versions.
- Supports symmetric and asymmetric keys for encryption, decryption, signing, and signature validation (/kms/docs/algorithms#key_purposes) .
- Functionality varies by key protection level.

Cloud HSM for Google Workspace (/kms/docs/onboard-hsm-workspace) Flat rate monthly fee for each instance, plus cost of active key versions and cryptographic operations. Use Multi-tenant Cloud HSM keys for client-side encryption in Google Workspace

- You control automatic key rotation schedule; IAM roles and permissions; enable, disable, or destroy key versions.
- Use symmetric keys for encryption and decryption.

Customer-supplied encryption keys (/docs/security/encryption/customer-supplied-encryption-keys) Might increase costs associated with Compute Engine or Cloud Storage

- Compute Engine (/compute/docs/disks/customer-supplied-encryption)
- Cloud Storage (/storage/docs/encryption/customer-supplied-keys)

- You provide key materials when needed.
- Key material resides in-memory - Google does not permanently store your keys on our servers.

Confidential Computing (/confidential-computing) Additional cost for each confidential VM; might increase log usage and associated costs

- Compute Engine (/confidential-computing/confidential-vm/docs)
- GKE (/kubernetes-engine/docs/how-to/confidential-gke-nodes)
- Dataproc (/dataproc/docs/concepts/configuring-clusters/confidential-compute)

- Provides encryption-in-use for VMs handling sensitive data or workloads.
- Keys can't be accessed by Google.

## Protecting data in Google Cloud

### Google-owned and Google-managed encryption keys (Google Cloud default encryption)

By default, data at rest in Google Cloud is protected by keys in Keystore, Google Cloud's internal key management service. Keys in Keystore are managed automatically by Google Cloud, with no configuration required on your part. Most services automatically rotate keys for you. Keystore supports a primary key version and a limited number of older key versions. The primary key version is used to encrypt new data encryption keys. Older key versions can still be used to decrypt existing data encryption keys. You can't view or manage these keys or review key usage logs. Data from multiple customers might use the same key encryption key.

This default encryption uses cryptographic modules that are validated to be FIPS 140-2 Level 1 (https://csrc.nist.gov/publications/detail/fips/140/2/final) compliant.

### Customer-managed encryption keys (CMEKs)

Cloud KMS keys that are used to protect your resources in CMEK-integrated services are customer-managed encryption keys (CMEKs). You can own and control CMEKs, while delegating key creation and assignment tasks to Cloud KMS Autokey. To learn more about automating provisioning for CMEKs, see Cloud Key Management Service with Autokey (/kms/docs/kms-autokey) .

You can use your Cloud KMS keys in compatible services (/kms/docs/compatible-services) to help you meet the following goals:

Own your encryption keys.

Control and manage your encryption keys, including choice of location, protection level, creation, access control, rotation, use, and destruction.

Selectively delete data protected by your keys in the case of off-boarding or to remediate security events (crypto-shredding).

Create dedicated, single-tenant keys that establish a cryptographic boundary around your data.

Log administrative and data access (/kms/docs/audit-logging) to encryption keys.

Meet current or future regulation that requires any of these goals.

When you use Cloud KMS keys with CMEK-integrated services (/kms/docs/cmek) , you can use organization policies to ensure that CMEKs are used as specified in the policies. For example, you can set an organization policy that ensures that your compatible Google Cloud resources use your Cloud KMS keys for encryption. Organization policies can also specify which project the key resources must reside in.

The features and level of protection provided depend on the protection level of the key:

Software keys - You can generate software keys in Cloud KMS and use them in all Google Cloud locations. You can create symmetric keys with automatic rotation (/kms/docs/key-rotation) or asymmetric keys with manual rotation. Customer-managed software keys use FIPS 140-2 Level 1 (https://csrc.nist.gov/publications/detail/fips/140/2/final) validated software cryptography modules. You also have control over the rotation period, Identity and Access Management (IAM) roles and permissions, and organization policies that govern your keys. You can use your software keys with many compatible Google Cloud resources (/kms/docs/compatible-services) .

Imported software keys - You can import software keys that you created elsewhere for use in Cloud KMS. You can import new key versions to manually rotate imported keys. You can use IAM roles and permissions and organization policies to govern usage of your imported keys.

Hardware keys with Multi-tenant Cloud HSM - You can generate hardware keys in a cluster of FIPS 140-2 Level 3 (https://csrc.nist.gov/publications/detail/fips/140/2/final) Hardware Security Modules (HSMs). You have control over the rotation period, IAM roles and permissions, and organization policies that govern your keys. When you create HSM keys using Cloud HSM, Google Cloud manages the HSM clusters so you don't have to. You can use your HSM keys with many compatible Google Cloud resources (/kms/docs/compatible-services) —the same services that support software keys. For the highest level of security compliance, use hardware keys.

Hardware keys with Single-tenant Cloud HSM - You can generate hardware keys in a cluster of dedicated partitions in FIPS 140-2 Level 3 (https://csrc.nist.gov/publications/detail/fips/140/2/final) Hardware Security Modules (HSMs) that you control. You have control over the rotation period, IAM roles and permissions, and organization policies that govern your keys. When you create a Single-tenant Cloud HSM instance, Google Cloud hosts the HSM clusters so you don't have to, but you control access to the instance and maintain it with a quorum of designated administrators. Instance operations require two-factor authentication using security keys that you own outside of Google Cloud. You can use your single-tenant HSM keys with many compatible Google Cloud resources (/kms/docs/compatible-services) —the same services that support software keys. For the highest level of security compliance with cryptographic isolation, use hardware keys.

External keys and Cloud EKM - You can use keys that reside in an external key manager (EKM). Cloud EKM lets you use keys held in a supported key manager (/kms/docs/ekm#supported_partners) to secure your Google Cloud resources. You can connect to your EKM over the internet (/kms/docs/ekm#internet) or over a Virtual Private Cloud (VPC) (/kms/docs/ekm#vpc) . Some Google Cloud services that support Cloud KMS keys don't support Cloud EKM keys.

To learn more about which Cloud KMS locations support which protection levels, see Cloud KMS locations (/kms/docs/locations) .

### Cloud KMS keys

You can use your Cloud KMS keys in custom applications using the Cloud KMS client libraries (/kms/docs/reference/libraries) or Cloud KMS API (/kms/docs/reference/rest) . The client libraries and API let you encrypt and decrypt data, sign data, and validate signatures.

### Multi-tenant Cloud HSM for Google Workspace

You can use your Multi-tenant Cloud HSM keys in Cloud HSM for Google Workspace to manage the keys used for client-side encryption (CSE) in Google Workspace. You can Onboard to Cloud HSM for Google Workspace (/kms/docs/onboard-hsm-workspace) .

### Customer-supplied encryption keys (CSEKs)

Cloud Storage (/storage) and Compute Engine (/compute) can use customer-supplied encryption keys (CSEKs) (/docs/security/encryption/customer-supplied-encryption-keys) . With customer-supplied encryption keys, you store the key material and provide it to Cloud Storage or Compute Engine when needed. Google Cloud does not store your CSEKs in any way.

### Confidential Computing

You can use the Confidential Computing platform to encrypt your data-in-use. Confidential Computing ensures that your data stays private and encrypted even while it's being processed.

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/) , and code samples are licensed under the Apache 2.0 License (https://www.apache.org/licenses/LICENSE-2.0) . For details, see the Google Developers Site Policies (https://developers.google.com/site-policies) . Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.


## Key rotation

Source: https://cloud.google.com/kms/docs/key-rotation

# Key rotation

This page discusses key rotation in Cloud Key Management Service. Key rotation is the process of creating new encryption keys to replace existing keys. By rotating your encryption keys on a regular schedule or after specific events, you can reduce the potential consequences of your key being compromised. For specific instructions to rotate a key, see Rotating keys (/kms/docs/rotate-key) .

## Why rotate keys?

For symmetric encryption, periodically and automatically rotating keys is a recommended security practice. Some industry standards, such as Payment Card Industry Data Security Standard (https://www.pcisecuritystandards.org/document_library?category=pcidss&document=pci_dss) (PCI DSS), require the regular rotation of keys.

Cloud Key Management Service does not support automatic rotation of asymmetric keys. See Considerations for asymmetric keys (#asymmetric) in this document.

Rotating keys provides several benefits:

Limiting the number of messages encrypted with the same key version helps prevent attacks enabled by cryptanalysis. Key lifetime recommendations depend on the key's algorithm, as well as either the number of messages produced or the total number of bytes encrypted with the same key version. For example, the recommended key lifetime for symmetric encryption keys in Galois/Counter Mode (GCM) is based on the number of messages encrypted, as noted at https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf .

In the event that a key is compromised, regular rotation limits the number of actual messages vulnerable to compromise.

If you suspect that a key version is compromised, disable it (/kms/docs/enable-disable) and revoke access to it (/kms/docs/iam) as soon as possible.

Regular key rotation ensures that your system is resilient to manual rotation, whether due to a security breach or the need to migrate your application to a stronger cryptographic algorithm. Validate your key rotation procedures before a real-life security incident occurs.

You can also manually rotate a key, either because it is compromised, or to modify your application to use a different algorithm.

## How often to rotate keys

We recommend that you rotate keys automatically (/kms/docs/rotate-key#automatic) on a regular schedule. A rotation schedule defines the frequency of rotation, and optionally the date and time when the first rotation occurs. The rotation schedule can be based on either the key's age or the number or volume of messages encrypted with a key version.

Some security regulations require periodic, automatic key rotation. Automatic key rotation at a defined period, such as every 90 days, increases security with minimal administrative complexity.

You should also manually rotate a key (/kms/docs/rotate-key#manual) if you suspect that it has been compromised, or when security guidelines require you to migrate an application to a stronger key algorithm. You can schedule a manual rotation for a date and time in the future. Manually rotating a key does not pause, modify, or otherwise impact an existing automatic rotation schedule for the key.

Don't rely on irregular or manual rotation as a primary component of your application's security.

## After you rotate keys

Rotating keys creates new active key versions, but doesn't re-encrypt your data and doesn't disable or delete previous key versions. Previous key versions remain active and incur costs until they are destroyed. Re-encrypting data removes your reliance on old key versions, allowing you to destroy them to avoid incurring additional costs. To learn how to re-encrypt your data, see Re-encrypting data (/kms/docs/re-encrypt-data) .

You must make sure that a key version is no longer in use (/kms/docs/destroy-restore#pre-destroy-checklist) before destroying the key version.

## Considerations for asymmetric keys

Cloud KMS does not support automatic rotation for asymmetric keys, because additional steps are required before you can use the new asymmetric key version.

For asymmetric keys used for signing , you must distribute the public key portion of the new key version. Afterward, you can specify the new key version in calls to the`CryptoKeyVersions.asymmetricSign` (/kms/docs/reference/rest/v1/projects.locations.keyRings.cryptoKeys.cryptoKeyVersions/asymmetricSign) method to create a signature, and update applications to use the new key version.

For asymmetric keys used for encryption , you must distribute and incorporate the public portion of the new key version into applications that encrypt data, and grant access to the private portion of the new key version, for applications that decrypt data.

## What's next

- Rotate a key (/kms/docs/rotate-key) .
- Enable or disable a key (/kms/docs/enable-disable) .
- Learn more about re-encrypting data (/kms/docs/re-encrypt-data) .

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/) , and code samples are licensed under the Apache 2.0 License (https://www.apache.org/licenses/LICENSE-2.0) . For details, see the Google Developers Site Policies (https://developers.google.com/site-policies) . Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.
