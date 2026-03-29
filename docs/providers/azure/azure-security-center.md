# Azure Security Center and Fundamentals

Source pages:
- Introduction to Azure security: https://learn.microsoft.com/en-us/azure/security/fundamentals/overview
- Azure encryption overview: https://learn.microsoft.com/en-us/azure/security/fundamentals/encryption-overview

## Introduction to Azure security

Source: https://learn.microsoft.com/en-us/azure/security/fundamentals/overview

# Introduction to Azure security

Security is critical in today's cloud environment. Cyber threats constantly evolve, and protecting your data, applications, and infrastructure requires a comprehensive, multilayered approach. Security is job one in the cloud, and it's important that you find accurate and timely information about Azure security.

This article provides a comprehensive look at the security available with Azure. For an end-to-end view of Azure security organized by protection, detection, and response capabilities, see End-to-end security in Azure (end-to-end) .

## Azure's defense-in-depth security approach

Azure employs a defense-in-depth strategy, providing multiple layers of security protection across the entire stack - from physical datacenters to compute, storage, networking, applications, and identity. This multilayered approach ensures that if one layer is compromised, additional layers continue to protect your resources.

Azure's infrastructure is meticulously crafted from the ground up, encompassing everything from physical facilities to applications, to securely host millions of customers simultaneously. This robust foundation empowers businesses to confidently meet their security requirements. For information on how Microsoft secures the Azure platform itself, see Azure infrastructure security . For details on physical datacenter security, see Azure physical security (physical-security) .

Azure is a public cloud service platform that supports a broad selection of operating systems, programming languages, frameworks, tools, databases, and devices. It can run Linux containers with Docker integration; build apps with JavaScript, Python, .NET, PHP, Java, and Node.js; and build back-ends for iOS, Android, and Windows devices. Azure public cloud services support the same technologies millions of developers and IT professionals already rely on and trust.

## Built-in platform security

Azure provides default security protections built into the platform that help protect your resources from the moment they're deployed. For comprehensive information on Azure's platform security capabilities, see Azure platform security overview .

- Network Protection : Azure DDoS Protection automatically shields your resources from distributed denial-of-service attacks.
- Encryption by Default : Data encryption at rest is enabled by default for Azure Storage, SQL Database, and many other services.
- Identity Security : Microsoft Entra ID provides secure authentication and authorization for all Azure services.
- Threat Detection : Built-in threat detection monitors for suspicious activities across your Azure resources.
- Compliance : Azure maintains the largest compliance portfolio in the industry, helping you meet regulatory requirements.

These foundational security controls work continuously in the background to protect your cloud infrastructure, with no extra configuration required for basic protection.

## Shared responsibility in the cloud

While Azure provides robust platform security, security in the cloud is a shared responsibility between Microsoft and you. The division of responsibilities depends on your deployment model (IaaS, PaaS, or SaaS):

- Microsoft's responsibility : Azure secures the underlying infrastructure, including physical datacenters, hardware, network infrastructure, and the host operating system.
- Your responsibility : You're responsible for securing your data, applications, identities, and access management.

Every workload and application is different, with unique security requirements based on industry regulations, data sensitivity, and business needs. This is where Azure's advanced security services play a role. For more information about the shared responsibility model, see Shared responsibility in the cloud (shared-responsibility) .

The primary focus of this document is on customer-facing controls that you can use to customize and increase security for your applications and services.

## Advanced security services for every workload

To meet your unique security requirements, Azure provides a comprehensive suite of advanced security services that you can configure and customize for your specific needs. These services are organized across six functional areas: Operations, Applications, Storage, Networking, Compute, and Identity. For a comprehensive catalog of security services and technologies, see Azure security services and technologies (services-technologies) .

In addition, Azure provides you with a wide array of configurable security options and the ability to control them so that you can customize security to meet the unique requirements of your organization's deployments. This document helps you understand how Azure security capabilities can help you fulfill these requirements.

For a structured view of Azure security controls and baselines, see the Microsoft cloud security benchmark (/en-us/security/benchmark/azure/introduction) , which provides comprehensive security guidance for Azure services. For information on Azure's technical security capabilities, see Azure security technical capabilities (technical-capabilities) .

### Compute security

Securing your virtual machines and compute resources is fundamental to protecting your workloads in Azure. Azure provides multiple layers of compute security, from hardware-based protections to software-based threat detection. For detailed virtual machine security information, see Azure Virtual Machines security overview (virtual-machines-overview) .

#### Trusted launch

Trusted launch (/en-us/azure/virtual-machines/trusted-launch) is the default for newly created Generation 2 Azure VMs and Virtual Machine Scale Sets. Trusted launch protects against advanced and persistent attack techniques including boot kits, rootkits, and kernel-level malware.

Trusted launch provides:

- Secure Boot : Protects against installation of malware-based rootkits and boot kits by ensuring only signed operating systems and drivers can boot
- vTPM (virtual Trusted Platform Module) : A dedicated secure vault for keys and measurements that enables attestation and boot integrity verification
- Boot Integrity Monitoring : Uses attestation through Microsoft Defender for Cloud to verify boot chain integrity and alert on failures

You can enable trusted launch on existing VMs and Virtual Machine Scale Sets.

#### Azure confidential computing

Azure confidential computing (/en-us/azure/confidential-computing/overview-azure-products) provides the final, missing piece of the data protection puzzle. It allows you to keep your data encrypted always - while at rest, when in motion through the network, and now, even while loaded in memory and in use. By making Remote Attestation (/en-us/azure/attestation/overview) possible, it also allows you to cryptographically verify that the VM you deploy booted securely and is configured correctly, before unlocking your data.

The spectrum of options ranges from enabling "lift and shift" scenarios of existing applications, to full control of security features. For Infrastructure as a Service (IaaS), you can use:

- Confidential virtual machines powered by AMD SEV-SNP (/en-us/azure/confidential-computing/confidential-vm-overview) : Hardware-based memory encryption with up to 256 GB encrypted memory
- Confidential VMs with Intel TDX (/en-us/azure/confidential-computing/tdx-confidential-vm-overview) : Intel Trust Domain Extensions providing enhanced performance and security
- Confidential VMs with NVIDIA H100 GPUs (/en-us/azure/confidential-computing/confidential-vm-overview) : GPU-accelerated confidential computing for AI/ML workloads
- Confidential application enclaves with Intel SGX (/en-us/azure/confidential-computing/application-development) : Application-level isolation for sensitive code and data

For Platform as a Service (PaaS), Azure offers multiple container-based confidential computing options (/en-us/azure/confidential-computing/choose-confidential-containers-offerings) , including integrations with Azure Kubernetes Service (AKS) (/en-us/azure/confidential-computing/confidential-nodes-aks-overview) .

#### Antimalware and antivirus

With Azure IaaS, you can use antimalware software from security vendors such as Microsoft, Symantec, Trend Micro, McAfee, and Kaspersky to protect your virtual machines from malicious files, adware, and other threats. Microsoft Antimalware (antimalware) for Azure Virtual Machines is a protection capability that helps identify and remove viruses, spyware, and other malicious software. Microsoft Antimalware provides configurable alerts when known malicious or unwanted software attempts to install itself or run on your Azure systems. You can also deploy Microsoft Antimalware by using Microsoft Defender for Cloud.

For modern protection, consider Microsoft Defender for Servers (/en-us/azure/defender-for-cloud/plan-defender-for-servers) which provides advanced threat protection including endpoint detection and response (EDR) through integration with Microsoft Defender for Endpoint.

#### Hardware security module

Encryption and authentication don't improve security unless the keys themselves are protected. You can simplify the management and security of your critical secrets and keys by storing them in Azure Key Vault (/en-us/azure/key-vault/general/overview) . Key Vault provides the option to store your keys in hardware security modules (HSMs) certified to FIPS 140-3 Level 3 (/en-us/azure/key-vault/keys/about-keys#compliance) standards. You can store your SQL Server encryption keys for backup or use with transparent data encryption (/en-us/sql/relational-databases/security/encryption/transparent-data-encryption) in Key Vault along with any keys or secrets from your applications. Microsoft Entra ID (/en-us/entra/identity/) manages permissions and access to these protected items.

For comprehensive information on key management options including Azure Key Vault, Managed HSM, and Payment HSM, see Key management in Azure (key-management) .

#### Virtual machine backup

Azure Backup (/en-us/azure/backup/backup-overview) is a solution that protects your application data with zero capital investment and minimal operating costs. Application errors can corrupt your data, and human errors can introduce bugs into your applications that can lead to security problems. With Azure Backup, your virtual machines running Windows and Linux are protected.

#### Azure Site Recovery

An important part of your organization's business continuity/disaster recovery (BCDR) (/en-us/azure/reliability/cross-region-replication-azure) strategy is figuring out how to keep corporate workloads and apps up and running when planned and unplanned outages occur. Azure Site Recovery (/en-us/azure/site-recovery/site-recovery-overview) helps orchestrate replication, failover, and recovery of workloads and apps so that they're available from a secondary location if your primary location goes down.

#### SQL VM TDE

Transparent data encryption (TDE) and column level encryption (CLE) are SQL server encryption features. This form of encryption requires you to manage and store the cryptographic keys used for encryption.

The Azure Key Vault (AKV) service is designed to improve the security and management of these keys in a secure and highly available location. The SQL Server Connector enables SQL Server to use these keys from Azure Key Vault.

If you're running SQL Server with on-premises machines, you can follow steps to access Azure Key Vault from your on-premises SQL Server instance. For SQL Server in Azure VMs, you can save time by using the Azure Key Vault Integration feature. By using a few Azure PowerShell cmdlets to enable this feature, you can automate the configuration necessary for a SQL VM to access your key vault.

For a comprehensive list of database security best practices, see Azure database security checklist (database-security-checklist) .

#### VM disk encryption

Important

Azure Disk Encryption is scheduled for retirement on September 15, 2028 . Until that date, you can continue to use Azure Disk Encryption without disruption. On September 15, 2028, ADE-enabled workloads will continue to run, but encrypted disks will fail to unlock after VM reboots, resulting in service disruption.

Use encryption at host (/en-us/azure/virtual-machines/disk-encryption) for new VMs, or consider Confidential VM sizes with OS disk encryption (/en-us/azure/confidential-computing/confidential-vm-overview#confidential-os-disk-encryption) for confidential computing workloads. All ADE-enabled VMs (including backups) must migrate to encryption at host before the retirement date to avoid service disruption. See Migrate from Azure Disk Encryption to encryption at host (/en-us/azure/virtual-machines/disk-encryption-migrate) for details.

For modern virtual machine encryption, Azure offers:

- Encryption at host : Provides end-to-end encryption for VM data, including temp disks and OS/data disk caches.
- Confidential disk encryption : Available with confidential VMs for hardware-based encryption.
- Server-side encryption with customer-managed keys : Manage your own encryption keys through Azure Key Vault or Azure Key Vault Managed HSM.

For more information, see Overview of managed disk encryption options (/en-us/azure/virtual-machines/disk-encryption-overview) .

#### Virtual networking

Virtual machines need network connectivity. To support that requirement, Azure requires virtual machines to be connected to an Azure Virtual Network. An Azure Virtual Network is a logical construct built on top of the physical Azure network fabric. Each logical Azure Virtual Network (/en-us/azure/virtual-network/virtual-networks-overview) is isolated from all other Azure Virtual Networks. This isolation helps ensure that network traffic in your deployments isn't accessible to other Microsoft Azure customers.

#### Patch updates

Patch updates provide the basis for finding and fixing potential problems and simplify the software update management process. They reduce the number of software updates you must deploy in your enterprise and increase your ability to monitor compliance.

#### Security policy management and reporting

Defender for Cloud (/en-us/azure/defender-for-cloud/defender-for-cloud-introduction) helps you prevent, detect, and respond to threats. It provides you increased visibility into, and control over, the security of your Azure resources. It provides integrated security monitoring and policy management across your Azure subscriptions. It helps detect threats that might otherwise go unnoticed, and works with a broad ecosystem of security solutions.

### Application security

Application security focuses on protecting your applications from threats throughout their lifecycle - from development to deployment and runtime. Azure provides comprehensive tools for secure development, testing, and protection of applications. For secure application development guidance, see Develop secure applications on Azure (/en-us/azure/security/develop/secure-develop) . For PaaS-specific security best practices, see Securing PaaS deployments (paas-deployments) . For IaaS deployment security, see Security best practices for IaaS workloads in Azure (iaas) .

#### Penetration testing

Microsoft doesn't perform penetration testing (pen-testing) of your application, but it understands that you want and need to perform testing on your own applications. You no longer need to notify Microsoft of pen testing activities, but you must still comply with the Microsoft Cloud Penetration Testing Rules of Engagement (https://www.microsoft.com/msrc/pentest-rules-of-engagement) .

#### Web application firewall

The Web Application Firewall (WAF) in Azure Application Gateway (/en-us/azure/web-application-firewall/ag/ag-overview) protects web applications against common web-based attacks such as SQL injection, cross-site scripting, and session hijacking. It's preconfigured to defend against the top 10 vulnerabilities identified by the Open Web Application Security Project (OWASP) (https://owasp.org/www-project-top-ten/) .

#### Authentication and authorization in Azure App Service

App Service Authentication / Authorization (/en-us/azure/app-service/overview-authentication-authorization) is a feature that provides a way for your application to sign in users so that you don't have to change code on the app backend. It provides an easy way to protect your application and work with per-user data.

#### Layered security architecture

Since App Service Environments (/en-us/azure/app-service/environment/app-service-app-service-environment-intro) provide an isolated runtime environment deployed into an Azure Virtual Network (/en-us/azure/virtual-network/virtual-networks-overview) , developers can create a layered security architecture providing differing levels of network access for each application tier. It's common to hide API back-ends from general Internet access, and only permit APIs to be called by upstream web apps. You can use Network Security groups (NSGs) (/en-us/azure/virtual-network/virtual-network-vnet-plan-design-arm) on Azure Virtual Network subnets containing App Service Environments to restrict public access to API applications.

App Service web apps (/en-us/azure/app-service/troubleshoot-diagnostic-logs) offer robust diagnostic capabilities for capturing logs from both the web server and the web application. These diagnostics are categorized into web server diagnostics and application diagnostics. Web server diagnostics include significant advancements for diagnosing and troubleshooting sites and applications.

The first new feature is real-time state information about application pools, worker processes, sites, application domains, and running requests. The second new feature is the detailed trace events that track a request throughout the complete request-and-response process.

To enable the collection of these trace events, you can configure IIS 7 to automatically capture comprehensive trace logs in XML format for specific requests. The collection can be based on elapsed time or error response codes.

### Storage security

Storage security is essential for protecting your data at rest and in transit. Azure provides multiple layers of encryption, access controls, and monitoring capabilities to ensure your data remains secure. For detailed information on data encryption, see Azure encryption overview (encryption-overview) . For key management options, see Key management in Azure (key-management) . For data encryption best practices, see Azure data security and encryption best practices (data-encryption-best-practices) .

#### Azure role-based access control (Azure RBAC)

You can secure your storage account by using Azure role-based access control (Azure RBAC) (../../role-based-access-control/overview) . To enforce security policies for data access, restrict access based on the need to know (https://en.wikipedia.org/wiki/Need_to_know) and least privilege (https://en.wikipedia.org/wiki/Principle_of_least_privilege) security principles. Grant these access rights by assigning the appropriate Azure role to groups and applications at a certain scope. Use Azure built-in roles (../../role-based-access-control/built-in-roles) , such as Storage Account Contributor, to assign privileges to users. You can control access to the storage keys for a storage account by using the Azure Resource Manager (../../storage/blobs/security-recommendations#data-protection) model through Azure RBAC.

#### Shared access signature

A shared access signature (SAS) (../../storage/common/storage-sas-overview) provides delegated access to resources in your storage account. By using the SAS, you can grant a client limited permissions to objects in your storage account for a specified period and with a specified set of permissions. Grant these limited permissions without having to share your account access keys.

#### Encryption in transit

Encryption in transit is a mechanism of protecting data when it's transmitted across networks. With Azure Storage, you can secure data by using:

Transport-level encryption (../../storage/blobs/security-recommendations) , such as HTTPS when you transfer data into or out of Azure Storage.

Wire encryption (../../storage/blobs/security-recommendations) , such as SMB 3.0 encryption (../../storage/blobs/security-recommendations) for Azure File shares (../../storage/files/storage-dotnet-how-to-use-files) .

Client-side encryption, to encrypt the data before it's transferred into storage and to decrypt the data after it's transferred out of storage.

#### Encryption at rest

For many organizations, data encryption at rest is a mandatory step towards data privacy, compliance, and data sovereignty. Three Azure storage security features provide encryption of data that is at rest:

Storage Service Encryption (../../storage/common/storage-service-encryption) automatically encrypts data when writing it to Azure Storage.

Client-side Encryption (../../storage/common/storage-client-side-encryption) also provides the feature of encryption at rest.

#### Storage analytics

Azure Storage Analytics (/en-us/rest/api/storageservices/fileservices/storage-analytics) performs logging and provides metrics data for a storage account. You can use this data to trace requests, analyze usage trends, and diagnose problems with your storage account. Storage Analytics logs detailed information about successful and failed requests to a storage service. You can use this information to monitor individual requests and to diagnose problems with a storage service. Requests are logged on a best-effort basis. The following types of authenticated requests are logged:

- Successful requests.
- Failed requests, including timeout, throttling, network, authorization, and other errors.
- Requests using a Shared Access Signature (SAS), including failed and successful requests.
- Requests to analytics data.

#### Enabling browser-based clients by using CORS

Cross-Origin Resource Sharing (CORS) (/en-us/rest/api/storageservices/fileservices/cross-origin-resource-sharing--cors--support-for-the-azure-storage-services) is a mechanism that allows domains to give each other permission for accessing each other's resources. The user agent sends extra headers to ensure that the JavaScript code loaded from a certain domain is allowed to access resources located at another domain. The latter domain then replies with extra headers allowing or denying the original domain access to its resources.

Azure storage services now support CORS. Once you set the CORS rules for the service, a properly authenticated request made against the service from a different domain is evaluated to determine whether it's allowed according to the rules you specify.

### Network security

Network security controls how traffic flows to and from your Azure resources. Azure provides a comprehensive set of network security services, from basic firewalling to advanced threat protection and global load balancing. For comprehensive network security information, see Azure network security overview (network-overview) . For network security best practices, see Azure network security best practices (network-best-practices) .

#### Network layer controls

Network access control is the act of limiting connectivity to and from specific devices or subnets and represents the core of network security. The goal of network access control is to make sure that your virtual machines and services are accessible only to users and devices you authorize.

##### Network security groups

A Network Security Group (NSG) (/en-us/azure/virtual-network/network-security-groups-overview) is a basic stateful packet filtering firewall. It enables you to control access based on a five-tuple. NSGs don't provide application layer inspection or authenticated access controls. You can use them to control traffic moving between subnets within an Azure Virtual Network and traffic between an Azure Virtual Network and the Internet.

##### Azure Firewall

Azure Firewall (/en-us/azure/firewall/overview) is a cloud-native and intelligent network firewall security service that provides threat protection for your cloud workloads running in Azure. It's a fully stateful firewall as a service with built-in high availability and unrestricted cloud scalability. It provides both east-west and north-south traffic inspection.

Azure Firewall is offered in three SKUs: Basic, Standard, and Premium:

- Azure Firewall Basic (/en-us/azure/firewall/basic-features) - Designed for small and medium-sized businesses, offering essential protection at an affordable price point.
- Azure Firewall Standard (/en-us/azure/firewall/features) - Provides L3-L7 filtering, threat intelligence feeds from Microsoft Cyber Security, and can scale to 30 Gbps.
- Azure Firewall Premium (/en-us/azure/firewall/premium-features) - Advanced threat protection for highly sensitive and regulated environments with:

- TLS Inspection : Decrypts outbound traffic, processes it for threats, then re-encrypts before sending to destination.
- IDPS (Intrusion Detection and Prevention System) : Signature-based IDPS with over 67,000 signatures in more than 50 categories, updated with 20-40+ new rules daily.
- URL Filtering : Extends FQDN filtering to consider the entire URL path.
- Advanced Web Categories : Enhanced categorization based on complete URLs for both HTTP and HTTPS traffic.
- Enhanced Performance : Scales up to 100 Gbps with 10 Gbps fat flow support.
- PCI DSS Compliance : Meets Payment Card Industry Data Security Standard requirements.

Azure Firewall Premium is essential for protecting against ransomware, as it can detect and block Command and Control (C&C) connectivity used by ransomware to fetch encryption keys. Learn more about ransomware protection with Azure Firewall (ransomware-protection-with-azure-firewall) .

##### Azure DDoS Protection

Azure DDoS Protection (/en-us/azure/ddos-protection/ddos-protection-overview) , combined with application design best practices, offers enhanced features to defend against DDoS attacks. It is automatically tuned to protect your specific Azure resources in a virtual network. Enabling protection is simple on any new or existing virtual network and requires no changes to your applications or resources.

Azure DDoS Protection offers two tiers: DDoS Network Protection and DDoS IP Protection.

DDoS Network Protection - Provides enhanced features to defend against Distributed Denial of Service (DDoS) attacks. It operates at network layers 3 and 4 and includes advanced features such as DDoS rapid response support, cost protection, and discounts on Web Application Firewall (WAF).

DDoS IP Protection - Follows a pay-per-protected IP model. It includes the same core engineering features as DDoS Network Protection but doesn't offer the additional services like DDoS rapid response support, cost protection, and WAF discounts.

##### Route control and forced tunneling

The ability to control routing behavior on your Azure Virtual Networks is a critical network security and access control capability. For example, if you want to make sure that all traffic to and from your Azure Virtual Network goes through that virtual security appliance, you need to be able to control and customize routing behavior. You can do this control and customization by configuring User-Defined Routes in Azure.

User-Defined Routes (/en-us/azure/virtual-network/virtual-networks-udr-overview#custom-routes) allow you to customize inbound and outbound paths for traffic moving into and out of individual virtual machines or subnets to ensure the most secure route possible. Forced tunneling (/en-us/azure/vpn-gateway/vpn-gateway-forced-tunneling-rm) is a mechanism you can use to ensure that your services aren't allowed to initiate a connection to devices on the Internet.

This restriction is different from being able to accept incoming connections and then responding to them. Front-end web servers need to respond to requests from Internet hosts. So, Internet-sourced traffic is allowed inbound to these web servers and the web servers can respond.

Commonly, use forced tunneling to force outbound traffic to the Internet to go through on-premises security proxies and firewalls.

##### Virtual network security appliances

While Network Security Groups, User-Defined Routes, and forced tunneling provide you with a level of security at the network and transport layers of the OSI model (https://en.wikipedia.org/wiki/OSI_model) , there might be times when you want to enable security at higher levels of the stack. You can access these enhanced network security features by using an Azure partner network security appliance solution. You can find the most current Azure partner network security solutions by visiting the Azure Marketplace (https://azuremarketplace.microsoft.com/marketplace/) and searching for security and network security .

#### Azure Virtual Network

An Azure virtual network (VNet) is a representation of your own network in the cloud. It's a logical isolation of the Azure network fabric dedicated to your subscription. You can fully control the IP address blocks, DNS settings, security policies, and route tables within this network. You can segment your VNet into subnets and place Azure IaaS virtual machines (VMs) on Azure Virtual Networks.

Additionally, you can connect the virtual network to your on-premises network using one of the connectivity options (/en-us/azure/vpn-gateway/) available in Azure. In essence, you can expand your network to Azure, with complete control on IP address blocks with the benefit of enterprise scale Azure provides.

Azure networking supports various secure remote access scenarios. Some of these scenarios include:

Connect individual workstations to an Azure Virtual Network (/en-us/azure/vpn-gateway/vpn-gateway-howto-point-to-site-rm-ps)

Connect on-premises network to an Azure Virtual Network with a VPN (/en-us/azure/vpn-gateway/tutorial-site-to-site-portal)

Connect on-premises network to an Azure Virtual Network with a dedicated WAN link (/en-us/azure/expressroute/expressroute-introduction)

Connect Azure Virtual Networks to each other (/en-us/azure/vpn-gateway/vpn-gateway-vnet-vnet-rm-ps)

#### Azure Virtual Network Manager

Azure Virtual Network Manager (/en-us/azure/virtual-network-manager/overview) provides a centralized solution for managing and securing your virtual networks at scale. It uses security admin rules (/en-us/azure/virtual-network-manager/concept-security-admins) to centrally define and enforce security policies across your entire organization. Security admin rules take precedence over network security group (NSG) rules and are applied on the virtual network. This precedence allows organizations to enforce core policies with security admin rules, while still enabling downstream teams to tailor NSGs according to their specific needs at the subnet and NIC levels.

Depending on the needs of your organization, use Allow , Deny , or Always Allow rule actions to enforce security policies:

Rule Action Description

Allow Allows the specified traffic by default. Downstream NSGs still receive this traffic and might deny it.

Always Allow Always allow the specified traffic, regardless of other rules with lower priority or NSGs. Use this rule to ensure that monitoring agent, domain controller, or management traffic isn't blocked.

Deny Block the specified traffic. Downstream NSGs don't evaluate this traffic after being denied by a security admin rule, ensuring your high-risk ports for existing and new virtual networks are protected by default.

In Azure Virtual Network Manager, network groups (/en-us/azure/virtual-network-manager/concept-network-groups) allow you to group virtual networks together for centralized management and enforcement of security policies. Network groups are a logical grouping of virtual networks based on your needs from a topology and security perspective. You can manually update the virtual network membership of your network groups or you can define conditional statements with Azure Policy (/en-us/azure/virtual-network-manager/concept-azure-policy-integration) to dynamically update network groups and automatically update your network group membership.

#### Azure Private Link

Azure Private Link (https://azure.microsoft.com/services/private-link/) enables you to access Azure PaaS Services (for example, Azure Storage and SQL Database) and Azure hosted customer-owned/partner services privately in your virtual network over a private endpoint (/en-us/azure/private-link/private-endpoint-overview) . Setup and consumption using Azure Private Link is consistent across Azure PaaS, customer-owned, and shared partner services. Traffic from your virtual network to the Azure service always remains on the Microsoft Azure backbone network.

By using private endpoints (/en-us/azure/private-link/private-endpoint-overview) , you can secure your critical Azure service resources to only your virtual networks. Azure Private Endpoint uses a private IP address from your virtual network to connect you privately and securely to a service powered by Azure Private Link, effectively bringing the service into your virtual network. Exposing your virtual network to the public internet is no longer necessary to consume services on Azure.

You can also create your own private link service in your virtual network. Azure Private Link service (/en-us/azure/private-link/private-link-service-overview) is the reference to your own service that is powered by Azure Private Link. Your service that is running behind Azure Standard Load Balancer can be enabled for Private Link access so that consumers to your service can access it privately from their own virtual networks. Your customers can create a private endpoint inside their virtual network and map it to this service. Exposing your service to the public internet is no longer necessary to render services on Azure.

#### VPN gateway

To send network traffic between your Azure Virtual Network and your on-premises site, you must create a VPN gateway for your Azure Virtual Network. A VPN gateway (/en-us/azure/vpn-gateway/vpn-gateway-about-vpngateways) is a type of virtual network gateway that sends encrypted traffic across a public connection. You can also use VPN gateways to send traffic between Azure Virtual Networks over the Azure network fabric.

#### ExpressRoute

Microsoft Azure ExpressRoute (/en-us/azure/expressroute/expressroute-introduction) is a dedicated WAN link that lets you extend your on-premises networks into the Microsoft cloud over a dedicated private connection facilitated by a connectivity provider.

With ExpressRoute, you can establish connections to Microsoft cloud services, such as Microsoft Azure and Microsoft 365. Connectivity can be from an any-to-any (IP VPN) network, a point-to-point Ethernet network, or a virtual cross-connection through a connectivity provider at a colocation facility.

ExpressRoute connections don't go over the public Internet and are more secure than VPN-based solutions. This design allows ExpressRoute connections to offer more reliability, faster speeds, lower latencies, and higher security than typical connections over the Internet.

#### Application gateway

Microsoft Azure Application Gateway (/en-us/azure/application-gateway/overview) provides an Application Delivery Controller (ADC) (https://en.wikipedia.org/wiki/Application_delivery_controller) as a service, offering various layer 7 load balancing capabilities for your application.

It allows you to optimize web farm productivity by offloading CPU intensive TLS termination to the Application Gateway (also known as TLS offload or TLS bridging ). It also provides other Layer 7 routing capabilities including round-robin distribution of incoming traffic, cookie-based session affinity, URL path-based routing, and the ability to host multiple websites behind a single Application Gateway. Azure Application Gateway is a layer-7 load balancer.

It provides failover, performance-routing HTTP requests between different servers, whether they are on the cloud or on-premises.

Application provides many Application Delivery Controller (ADC) features including HTTP load balancing, cookie-based session affinity, TLS offload (/en-us/azure/web-application-firewall/ag/tutorial-restrict-web-traffic-powershell) , custom health probes, support for multi-site, and many others.

#### Web application firewall

Web Application Firewall is a feature of Azure Application Gateway (/en-us/azure/application-gateway/overview) that protects web applications that use application gateway for standard Application Delivery Control (ADC) functions. Web application firewall protects them against most of the OWASP top 10 common web vulnerabilities.

SQL injection protection

Protection against common web attacks such as command injection, HTTP request smuggling, HTTP response splitting, and remote file inclusion

Protection against HTTP protocol violations

Protection against HTTP protocol anomalies, such as missing host, user-agent, and accept headers

Prevention against bots, crawlers, and scanners

Detection of common application misconfigurations (for example, Apache, IIS)

A centralized web application firewall (WAF) simplifies security management and enhances protection against web attacks. It provides better assurance against intrusion threats and can respond faster to security threats by patching known vulnerabilities centrally, rather than securing each individual web application. You can easily upgrade existing application gateways to include a web application firewall.

#### Azure Front Door

Azure Front Door (/en-us/azure/frontdoor/front-door-overview) is a global, scalable entry point that uses Microsoft's global edge network to create fast, secure, and widely scalable web applications. Front Door provides:

- Global load balancing : Distribute traffic across multiple backends in different regions
- Integrated Web Application Firewall : Protect against common web vulnerabilities and attacks
- DDoS protection : Built-in protection against distributed denial-of-service attacks
- SSL/TLS offload : Centralized certificate management and traffic encryption
- URL-based routing : Route traffic to different backends based on URL patterns

Front Door combines content delivery, application acceleration, and security into a single service.

#### Traffic manager

Microsoft Azure Traffic Manager (/en-us/azure/traffic-manager/traffic-manager-overview) allows you to control the distribution of user traffic for service endpoints in different datacenters. Service endpoints that Traffic Manager supports include Azure VMs, Web Apps, and Cloud services. You can also use Traffic Manager with external, non-Azure endpoints.

Traffic Manager uses the Domain Name System (DNS) to direct client requests to the most appropriate endpoint based on a traffic-routing method (/en-us/azure/traffic-manager/traffic-manager-routing-methods) and the health of the endpoints. Traffic Manager provides a range of traffic-routing methods to suit different application needs, endpoint health monitoring (/en-us/azure/traffic-manager/traffic-manager-monitoring) , and automatic failover. Traffic Manager is resilient to failure, including the failure of an entire Azure region.

#### Azure Load Balancer

Azure Load Balancer (/en-us/azure/load-balancer/load-balancer-overview) delivers high availability and network performance to your applications. It's a Layer 4 (TCP, UDP) load balancer that distributes incoming traffic among healthy instances of services defined in a load-balanced set. You can configure Azure Load Balancer to:

Load balance incoming Internet traffic to virtual machines. This configuration is known as public load balancing (/en-us/azure/load-balancer/components#frontend-ip-configurations) .

Load balance traffic between virtual machines in a virtual network, between virtual machines in cloud services, or between on-premises computers and virtual machines in a cross-premises virtual network. This configuration is known as internal load balancing (/en-us/azure/load-balancer/components#frontend-ip-configurations) .

Forward external traffic to a specific virtual machine

#### Internal DNS

You can manage the list of DNS servers used in a VNet in the Azure portal, or in the network configuration file. You can add up to 12 DNS servers for each VNet. When specifying DNS servers, verify that you list your DNS servers in the correct order for your environment. DNS server lists don't work round-robin. They're used in the order that you specify. If the first DNS server on the list is reachable, the client uses that DNS server regardless of whether the DNS server is functioning properly or not. To change the DNS server order for your virtual network, remove the DNS servers from the list and add them back in the order that you want. DNS supports the availability aspect of the “CIA” security triad.

#### Azure DNS

The Domain Name System, or DNS, is responsible for translating (or resolving) a website or service name to its IP address. Azure DNS (/en-us/azure/dns/dns-overview) is a hosting service for DNS domains, providing name resolution using Microsoft Azure infrastructure. By hosting your domains in Azure, you can manage your DNS records using the same credentials, APIs, tools, and billing as your other Azure services. DNS supports the availability aspect of the "CIA" security triad.

#### Azure Monitor logs NSGs

You can enable the following diagnostic log categories for NSGs:

Event: Contains entries for which NSG rules are applied to VMs and instance roles based on MAC address. The status for these rules is collected every 60 seconds.

Rules counter: Contains entries for how many times each NSG rule is applied to deny or allow traffic.

#### Microsoft Defender for Cloud

Microsoft Defender for Cloud (../../security-center/security-center-introduction) continuously analyzes the security state of your Azure resources for network security best practices. When Defender for Cloud identifies potential security vulnerabilities, it creates recommendations (../../security-center/security-center-recommendations) that guide you through the process of configuring the needed controls to harden and protect your resources.

#### Advanced Container Networking Services (ACNS)

Advanced Container Networking Services (ACNS) (/en-us/azure/security/fundamentals/overview#networking) is a comprehensive suite designed to elevate the operational efficiency of your Azure Kubernetes Service (AKS) clusters. It provides advanced security and observability features, addressing the complexities of managing microservices infrastructure at scale.

These features are divided into two main pillars:

Security : For clusters using Azure CNI Powered by Cilium, network policies include fully qualified domain name (FQDN) filtering for solving the complexities of maintaining configuration.

Observability : This feature of the Advanced Container Networking Services suite brings the power of Hubble's control plane to both Cilium and non-Cilium Linux data planes, providing enhanced visibility into networking and performance.

## Security operations and management

Managing and monitoring the security of your Azure environment is essential for maintaining a strong security posture. Azure provides comprehensive tools for security operations, threat detection, and incident response. For detailed coverage of security management and monitoring, see Azure security management and monitoring overview (management-monitoring-overview) . For operational security best practices, see Azure operational security best practices (operational-best-practices) . For a comprehensive operational security overview, see Azure operational security overview (operational-overview) .

### Microsoft Sentinel

Microsoft Sentinel (/en-us/azure/sentinel/overview) is a scalable, cloud-native security information and event management (SIEM) and security orchestration, automation, and response (SOAR) solution. Microsoft Sentinel delivers intelligent security analytics and threat intelligence across the enterprise, providing a single solution for attack detection, threat visibility, proactive hunting, and threat response.

Microsoft Sentinel is now available in the Microsoft Defender portal for all customers, offering a unified security operations experience that streamlines workflows and enhances visibility. The integration with Security Copilot enables analysts to interact with Microsoft Sentinel data using natural language, generate hunting queries, and automate investigations for faster threat response.

#### Microsoft Defender for Cloud

Microsoft Defender for Cloud (/en-us/azure/defender-for-cloud/defender-for-cloud-introduction) helps you prevent, detect, and respond to threats by giving you increased visibility into and control over the security of your Azure resources. Microsoft Defender for Cloud provides integrated security monitoring and policy management across your Azure subscriptions, helps detect threats that might otherwise go unnoticed, and works with a broad ecosystem of security solutions.

Microsoft Defender for Cloud offers comprehensive protection with workload-specific plans including:

- Defender for Servers - Advanced threat protection for Windows and Linux servers
- Defender for Containers - Security for containerized applications and Kubernetes
- Defender for Storage - Threat detection with malware scanning and sensitive data discovery
- Defender for Databases - Protection for Azure SQL, Azure Database for MySQL, and PostgreSQL
- Defender for Foundry Tools - Runtime protection for Foundry Tools against jailbreak attempts, data exposure, and suspicious access patterns
- Defender CSPM - Cloud Security Posture Management with attack path analysis, security governance, and AI security posture management

In addition, Defender for Cloud helps with security operations by providing you with a single dashboard that surfaces alerts and recommendations that you can act on immediately. Security Copilot integration provides AI-generated summaries, remediation scripts, and delegation capabilities to accelerate risk remediation.

For comprehensive threat detection capabilities across Azure, see Azure threat protection (threat-detection) .

### VM disk encryption

By default, encryption at host (/en-us/azure/virtual-machines/disk-encryption) helps you encrypt your IaaS virtual machine disks. It provides server-side encryption at the VM host level by using AES 256 encryption, which is FIPS 140-2 compliant. This encryption occurs without consuming VM CPU resources and provides end-to-end encryption for temporary disks, OS/data disk caches, and data flows to Azure Storage. By default, it uses platform-managed keys with no additional configuration required. Optionally, you can configure the solution with customer-managed keys stored in Azure Key Vault or Azure Key Vault Managed HSM when you need to control and manage your own disk-encryption keys. The solution ensures that all data on the virtual machine disks are encrypted at rest in your Azure storage. For more information on key management options, see Key management in Azure (key-management) .

### Azure Resource Manager

Azure Resource Manager (/en-us/azure/azure-resource-manager/management/overview) enables you to work with the resources in your solution as a group. You can deploy, update, or delete all the resources for your solution in a single, coordinated operation. You use an Azure Resource Manager template (/en-us/azure/azure-resource-manager/templates/overview) for deployment, and that template can work for different environments such as testing, staging, and production. Resource Manager provides security, auditing, and tagging features to help you manage your resources after deployment.

Azure Resource Manager template-based deployments help improve the security of solutions deployed in Azure because standard security control settings can be integrated into standardized template-based deployments. Templates reduce the risk of security configuration errors that might take place during manual deployments.

### Application Insights

Application Insights (/en-us/azure/azure-monitor/app/app-insights-overview) is a flexible Application Performance Management (APM) service designed for web developers. It enables you to monitor your live web applications and automatically detect performance issues. By using powerful analytics tools, you can diagnose problems and gain insights into user interactions with your apps. Application Insights monitors your application continuously, from development through testing and into production.

Application Insights generates insightful charts and tables that reveal peak user activity times, app responsiveness, and the performance of any external services it relies on.

If there are crashes, failures, or performance issues, you can search through the data in detail to diagnose the cause. The service sends you emails if there are any changes in the availability and performance of your app. Application Insight thus becomes a valuable security tool because it helps with the availability in the confidentiality, integrity, and availability security triad.

### Azure Monitor

Azure Monitor (/en-us/azure/azure-monitor/overview) offers visualization, query, routing, alerting, autoscale, and automation on data both from the Azure subscription (Activity Log (/en-us/azure/azure-monitor/essentials/platform-logs-overview) ) and each individual Azure resource (Resource Logs (/en-us/azure/azure-monitor/essentials/platform-logs-overview) ). You can use Azure Monitor to alert you on security-related events that are generated in Azure logs.

### Azure Monitor logs

Azure Monitor logs (/en-us/azure/azure-monitor/logs/log-query-overview) provides an IT management solution for both on-premises and third-party cloud-based infrastructure (such as Amazon Web Services) in addition to Azure resources. Data from Azure Monitor can be routed directly to Azure Monitor logs so you can see metrics and logs for your entire environment in one place.

Azure Monitor logs can be a useful tool in forensic and other security analysis, as the tool enables you to quickly search through large amounts of security-related entries with a flexible query approach. In addition, on-premises firewall and proxy logs can be exported into Azure and made available for analysis by using Azure Monitor logs. (/en-us/azure/azure-monitor/agents/agent-windows)

### Azure Advisor

Azure Advisor (/en-us/azure/advisor/advisor-overview) is a personalized cloud consultant that helps you optimize your Azure deployments. It analyzes your resource configuration and usage data. It then recommends solutions to help improve the performance (/en-us/azure/advisor/advisor-performance-recommendations) , security (/en-us/azure/advisor/advisor-security-recommendations) , and reliability (/en-us/azure/advisor/advisor-high-availability-recommendations) of your resources while looking for opportunities to reduce your overall Azure spend (/en-us/azure/advisor/advisor-cost-recommendations) . Azure Advisor provides security recommendations, which can significantly improve your overall security posture for solutions you deploy in Azure. These recommendations are drawn from security analysis performed by Microsoft Defender for Cloud (/en-us/azure/defender-for-cloud/defender-for-cloud-introduction) .

## Identity and access management

Identity is the primary security perimeter in cloud computing. Protecting identities and controlling access to resources is fundamental to securing your Azure environment. Microsoft Entra ID provides comprehensive identity and access management capabilities. For detailed information, see Azure identity management overview (identity-management-overview) . For identity management best practices, see Azure identity management and access control security best practices (identity-management-best-practices) . For guidance on securing identity infrastructure, see Five steps to securing your identity infrastructure (steps-secure-identity) .

### Microsoft Entra ID

Microsoft Entra ID (/en-us/entra/identity/) is Microsoft's cloud-based identity and access management service. It provides:

- Single Sign-On (SSO) : Enable users to access multiple applications with one set of credentials
- Multi-Factor Authentication (MFA) : Require multiple forms of verification to sign in
- Conditional Access : Control access to resources based on user, device, location, and risk
- Identity Protection : Detect and respond to identity-based risks
- Privileged Identity Management (PIM) : Provide just-in-time privileged access to Azure resources
- Identity Governance : Manage identity lifecycle and access rights

### Role-based access control (RBAC)

Azure role-based access control (RBAC) helps you manage who has access to Azure resources, what they can do with those resources, and what areas they have access to. RBAC provides fine-grained access management for Azure resources, enabling you to grant users only the rights they need to perform their jobs.

### Microsoft Entra Privileged Identity Management

Microsoft Entra Privileged Identity Management (PIM) (/en-us/entra/id-governance/privileged-identity-management/) enables you to manage, control, and monitor access to important resources in your organization. PIM provides time-based and approval-based role activation to mitigate the risks of excessive, unnecessary, or misused access permissions.

### Managed identities for Azure resources

Managed identities (/en-us/entra/identity/managed-identities-azure-resources/overview) for Azure resources provide Azure services with an automatically managed identity in Microsoft Entra ID. Use this identity to authenticate to any service that supports Microsoft Entra authentication, without having credentials in your code.

Patch updates provide the basis for finding and fixing potential problems and simplify the software update management process. They reduce the number of software updates you must deploy in your enterprise and increase your ability to monitor compliance.

### Security policy management and reporting

Defender for Cloud (/en-us/azure/defender-for-cloud/defender-for-cloud-introduction) helps you prevent, detect, and respond to threats. It provides you increased visibility into, and control over, the security of your Azure resources. It provides integrated security monitoring and policy management across your Azure subscriptions. It helps detect threats that might otherwise go unnoticed, and works with a broad ecosystem of security solutions.

### Secure identity

Microsoft uses multiple security practices and technologies across its products and services to manage identity and access.

Multifactor authentication (https://www.microsoft.com/security/business/identity-access/microsoft-entra-mfa-multi-factor-authentication) requires users to use multiple methods for access, on-premises and in the cloud. It provides strong authentication with a range of easy verification options, while accommodating users with a simple sign-in process.

Microsoft Authenticator (https://aka.ms/authenticator) provides a user-friendly multifactor authentication experience that works with both Microsoft Entra ID and Microsoft accounts. It includes support for wearables and fingerprint-based approvals.

Password policy enforcement (/en-us/entra/identity/authentication/concept-sspr-policy) increases the security of traditional passwords by imposing length and complexity requirements, forced periodic rotation, and account lockout after failed authentication attempts.

Token-based authentication (/en-us/entra/identity-platform/authentication-vs-authorization) enables authentication via Microsoft Entra ID.

Azure role-based access control (Azure RBAC) (../../role-based-access-control/built-in-roles) enables you to grant access based on the user’s assigned role. It's easy to give users only the amount of access they need to perform their job duties. You can customize Azure RBAC per your organization’s business model and risk tolerance.

Integrated identity management (hybrid identity) (/en-us/entra/identity/hybrid/plan-hybrid-identity-design-considerations-overview.md) enables you to maintain control of users’ access across internal datacenters and cloud platforms. It creates a single user identity for authentication and authorization to all resources.

### Secure apps and data

Microsoft Entra ID (https://www.microsoft.com/security/business/identity-access/microsoft-entra-id) , a comprehensive identity and access management cloud solution, helps secure access to data in applications on site and in the cloud, and simplifies the management of users and groups. It combines core directory services, advanced identity governance, security, and application access management, and makes it easy for developers to build policy-based identity management into their apps. To enhance your Microsoft Entra ID, you can add paid capabilities by using the Microsoft Entra Basic, Premium P1, and Premium P2 editions.

Free or common features Basic features Premium P1 features Premium P2 features Microsoft Entra join – Windows 10 only related features

Directory Objects (/en-us/entra/fundamentals/active-directory-whatis.md) , User/Group Management (add/update/delete)/ User-based provisioning, Device registration (/en-us/entra/fundamentals/active-directory-whatis.md) , single sign-on (SSO) (/en-us/entra/fundamentals/active-directory-whatis.md) , Self-Service Password Change for cloud users (/en-us/entra/fundamentals/active-directory-whatis.md) , Connect (Sync engine that extends on-premises directories to Microsoft Entra ID) (/en-us/entra/fundamentals/active-directory-whatis.md) , Security / Usage Reports (/en-us/entra/fundamentals/active-directory-whatis.md) Group-based access management / provisioning (/en-us/entra/fundamentals/active-directory-whatis.md) , Self-Service Password Reset for cloud users (/en-us/entra/fundamentals/active-directory-whatis.md) , Company Branding (sign in Pages/Access Panel customization) (/en-us/entra/fundamentals/active-directory-whatis.md) , Application Proxy (/en-us/entra/fundamentals/active-directory-whatis.md) , SLA 99.9% (/en-us/entra/fundamentals/active-directory-whatis.md) Self-Service Group and app Management/Self-Service application additions/Dynamic Groups (/en-us/entra/fundamentals/active-directory-whatis.md) , Self-Service Password Reset/Change/Unlock with on-premises write-back (/en-us/entra/fundamentals/active-directory-whatis.md) , multifactor authentication (Cloud and On-premises (MFA Server)) (/en-us/entra/fundamentals/active-directory-whatis.md) , MIM CAL + MIM Server (/en-us/entra/fundamentals/active-directory-whatis.md) , Cloud App Discovery (/en-us/entra/fundamentals/active-directory-whatis.md) , Connect Health (/en-us/entra/fundamentals/active-directory-whatis.md) , Automatic password rollover for group accounts (/en-us/entra/fundamentals/active-directory-whatis.md) Identity Protection (/en-us/entra/id-protection/overview-identity-protection) , Privileged Identity Management (/en-us/entra/id-governance/privileged-identity-management/pim-configure) Join a device to Microsoft Entra ID, Desktop SSO, Microsoft Passport for Microsoft Entra ID, Administrator BitLocker recovery (/en-us/entra/fundamentals/active-directory-whatis.md) , MDM autoenrollment, Self-Service BitLocker recovery, extra local administrators to Windows 10 devices via Microsoft Entra join (/en-us/entra/fundamentals/active-directory-whatis.md)

Cloud App Discovery (/en-us/cloud-app-security/set-up-cloud-discovery) is a premium feature of Microsoft Entra ID that enables you to identify cloud applications that employees in your organization use.

Microsoft Entra ID Protection (/en-us/entra/id-protection/overview-identity-protection) is a security service that uses Microsoft Entra anomaly detection capabilities to provide a consolidated view into risk detections and potential vulnerabilities that could affect your organization’s identities.

Microsoft Entra Domain Services (https://azure.microsoft.com/products/microsoft-entra-ds/) enables you to join Azure VMs to a domain without the need to deploy domain controllers. Users sign in to these VMs by using their corporate Active Directory credentials, and can seamlessly access resources.

Microsoft Entra B2C (https://www.microsoft.com/security/business/identity-access/microsoft-entra-id) is a highly available, global identity management service for consumer-facing apps that can scale to hundreds of millions of identities and integrate across mobile and web platforms. Your customers can sign in to all your apps through customizable experiences that use existing social media accounts, or you can create new standalone credentials.

Microsoft Entra B2B Collaboration (/en-us/entra/external-id/what-is-b2b) is a secure partner integration solution that supports your cross-company relationships by enabling partners to access your corporate applications and data selectively by using their self-managed identities.

Microsoft Entra joined (/en-us/entra/identity/devices/overview) enables you to extend cloud capabilities to Windows 10 devices for centralized management. It makes it possible for users to connect to the corporate or organizational cloud through Microsoft Entra ID and simplifies access to apps and resources.

Microsoft Entra application proxy (/en-us/entra/identity/app-proxy/application-proxy.md) provides SSO and secure remote access for web applications hosted on-premises.

## Next steps

Understand your shared responsibility in the cloud (shared-responsibility) .

Learn how Microsoft Defender for Cloud (../../security-center/security-center-introduction) can help you prevent, detect, and respond to threats by providing increased visibility and control over the security of your Azure resources.

Explore Azure security best practices and patterns (best-practices-and-patterns) for additional security recommendations.

Review the Microsoft cloud security benchmark (/en-us/security/benchmark/azure/introduction) for comprehensive security guidance.

See End-to-end security in Azure (end-to-end) for a protection, detection, and response view of Azure security architecture.

## Feedback

Was this page helpful?

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

## Additional resources

- Last updated on 2026-01-12


## Azure encryption overview

Source: https://learn.microsoft.com/en-us/azure/security/fundamentals/encryption-overview

# Azure encryption overview

This article provides an overview of how encryption is used in Microsoft Azure. It covers the major areas of encryption, including encryption at rest, encryption in flight, and key management with Azure Key Vault.

## Encryption of data at rest

Data at rest includes information that resides in persistent storage on physical media, in any digital format. Microsoft Azure offers a variety of data storage solutions to meet different needs, including file, disk, blob, and table storage. Microsoft also provides encryption to protect Azure SQL Database (/en-us/azure/azure-sql/database/sql-database-paas-overview) , Azure Cosmos DB (/en-us/azure/cosmos-db/database-encryption-at-rest) , and Azure Data Lake.

You can use AES 256 encryption to protect data at rest for services across the software as a service (SaaS), platform as a service (PaaS), and infrastructure as a service (IaaS) cloud models.

For a more detailed discussion of how Azure encrypts data at rest, see Azure Data Encryption at Rest (encryption-atrest) .

## Azure encryption models

Azure supports various encryption models, including server-side encryption that uses service-managed keys, customer-managed keys in Key Vault, or customer-managed keys on customer-controlled hardware. By using client-side encryption, you can manage and store keys on-premises or in another secure location.

### Client-side encryption

You perform client-side encryption outside of Azure. It includes:

- Data encrypted by an application that's running in your datacenter or by a service application
- Data that is already encrypted when Azure receives it

By using client-side encryption, cloud service providers don't have access to the encryption keys and can't decrypt this data. You maintain complete control of the keys.

### Server-side encryption

The three server-side encryption models offer different key management characteristics:

- Service-managed keys : Provides a combination of control and convenience with low overhead.
- Customer-managed keys : Gives you control over the keys, including Bring Your Own Keys (BYOK) support, or allows you to generate new ones.
- Service-managed keys in customer-controlled hardware : Enables you to manage keys in your proprietary repository, outside of Microsoft control (also called Host Your Own Key or HYOK).

### Azure Disk Encryption

Important

Azure Disk Encryption is scheduled for retirement on September 15, 2028 . Until that date, you can continue to use Azure Disk Encryption without disruption. On September 15, 2028, ADE-enabled workloads will continue to run, but encrypted disks will fail to unlock after VM reboots, resulting in service disruption.

Use encryption at host (/en-us/azure/virtual-machines/disk-encryption) for new VMs, or consider Confidential VM sizes with OS disk encryption (/en-us/azure/confidential-computing/confidential-vm-overview#confidential-os-disk-encryption) for confidential computing workloads. All ADE-enabled VMs (including backups) must migrate to encryption at host before the retirement date to avoid service disruption. See Migrate from Azure Disk Encryption to encryption at host (/en-us/azure/virtual-machines/disk-encryption-migrate) for details.

All Managed Disks, Snapshots, and Images are encrypted by default using Storage Service Encryption with a service-managed key. For virtual machines, encryption at host provides end-to-end encryption for your VM data, including temporary disks and OS/data disk caches. Azure also offers options to manage keys in Azure Key Vault. For more information, see Overview of managed disk encryption options (/en-us/azure/virtual-machines/disk-encryption-overview) .

### Azure Storage Service Encryption

You can encrypt data at rest in Azure Blob storage and Azure file shares for both server-side and client-side scenarios.

Azure Storage Service Encryption (SSE) (/en-us/azure/storage/common/storage-service-encryption) automatically encrypts data before it is stored and automatically decrypts the data when you retrieve it. Storage Service Encryption uses 256-bit AES encryption, one of the strongest block ciphers available.

### Azure SQL Database encryption

Azure SQL Database (/en-us/azure/azure-sql/database/sql-database-paas-overview) is a general-purpose relational database service that supports structures such as relational data, JSON, spatial, and XML. SQL Database supports both server-side encryption through the Transparent Data Encryption (TDE) feature and client-side encryption through the Always Encrypted feature.

#### Transparent Data Encryption

TDE (/en-us/sql/relational-databases/security/encryption/transparent-data-encryption-tde) encrypts SQL Server (https://www.microsoft.com/sql-server) , Azure SQL Database (/en-us/azure/azure-sql/database/sql-database-paas-overview) , and Azure Synapse Analytics (/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-overview-what-is) data files in real time by using a Database Encryption Key (DEK). TDE is enabled by default on newly created Azure SQL databases.

#### Always Encrypted

The Always Encrypted (/en-us/sql/relational-databases/security/encryption/always-encrypted-database-engine) feature in Azure SQL lets you encrypt data within client applications before storing it in Azure SQL Database. You can enable delegation of on-premises database administration to third parties while maintaining separation between those who own and can view the data and those who manage it.

#### Cell-level or column-level encryption

With Azure SQL Database, you can apply symmetric encryption to a column of data by using Transact-SQL. This approach is called cell-level encryption or column-level encryption (CLE) (/en-us/sql/relational-databases/security/encryption/encrypt-a-column-of-data) , because you can use it to encrypt specific columns or cells with different encryption keys. This approach gives you more granular encryption capability than TDE.

### Azure Cosmos DB database encryption

Azure Cosmos DB (/en-us/azure/cosmos-db/database-encryption-at-rest) is Microsoft's globally distributed, multi-model database. User data stored in Azure Cosmos DB in non-volatile storage (solid-state drives) is encrypted by default by using service-managed keys. You can add a second layer of encryption with your own keys by using the customer-managed keys (CMK) (/en-us/azure/cosmos-db/how-to-setup-cmk) feature.

### Encryption at rest in Azure Data Lake

Azure Data Lake (../../data-lake-store/data-lake-store-encryption) is an enterprise-wide repository of every type of data collected in a single place prior to any formal definition of requirements or schema. Data Lake Store supports transparent encryption at rest that's on by default and set up during the creation of your account. By default, Azure Data Lake Store manages the keys for you, but you can choose to manage them yourself.

Three types of keys are used in encrypting and decrypting data: the Master Encryption Key (MEK), Data Encryption Key (DEK), and Block Encryption Key (BEK). The MEK encrypts the DEK, which is stored on persistent media, and the BEK is derived from the DEK and the data block. If you manage your own keys, you can rotate the MEK.

## Encryption of data in transit

Azure provides many mechanisms for keeping data private as it moves from one location to another.

### Data-link layer encryption

Whenever Azure customer traffic moves between datacenters - outside physical boundaries not controlled by Microsoft - a data-link layer encryption method using the IEEE 802.1AE MAC Security Standards (https://1.ieee802.org/security/802-1ae/) (also known as MACsec) is applied from point-to-point across the underlying network hardware. The devices encrypt the packets before sending them, which prevents physical "man-in-the-middle" or snooping/wiretapping attacks. This MACsec encryption is on by default for all Azure traffic traveling within a region or between regions.

### TLS encryption

Microsoft gives customers the ability to use Transport Layer Security (TLS) (https://en.wikipedia.org/wiki/Transport_Layer_Security) protocol to protect data when it's traveling between cloud services and customers. Microsoft datacenters negotiate a TLS connection with client systems that connect to Azure services. TLS provides strong authentication, message privacy, and integrity.

Important

Azure is transitioning to require TLS 1.2 or later for all connections to Azure services. Most Azure services completed this transition by August 31, 2025. Ensure your applications use TLS 1.2 or later.

Perfect Forward Secrecy (PFS) (https://en.wikipedia.org/wiki/Forward_secrecy) protects connections between customers' client systems and Microsoft cloud services by unique keys. Connections support RSA-based 2,048-bit key lengths, ECC 256-bit key lengths, SHA-384 message authentication, and AES-256 data encryption.

### Azure Storage transactions

When you interact with Azure Storage through the Azure portal, all transactions take place over HTTPS. You can also use the Storage REST API over HTTPS to interact with Azure Storage. You can enforce the use of HTTPS when you call the REST APIs by enabling the secure transfer requirement for the storage account.

Shared Access Signatures (SAS) (/en-us/azure/storage/common/storage-sas-overview) , which you can use to delegate access to Azure Storage objects, include an option to specify that only the HTTPS protocol can be used.

### SMB encryption

SMB 3.0 (/en-us/previous-versions/windows/it-pro/windows-server-2012-R2-and-2012/dn551363(v=ws.11)#BKMK_SMBEncryption) , used to access Azure Files shares, supports encryption and is available in Windows Server 2012 R2, Windows 8, Windows 8.1, and Windows 10. It supports cross-region access and access on the desktop.

### VPN encryption

You can connect to Azure through a virtual private network that creates a secure tunnel to protect the privacy of the data sent across the network.

#### Azure VPN gateways

Azure VPN gateway (/en-us/azure/vpn-gateway/vpn-gateway-about-vpn-gateway-settings) sends encrypted traffic between your virtual network and your on-premises location across a public connection, or between virtual networks. Site-to-site VPNs use IPsec (https://en.wikipedia.org/wiki/IPsec) for transport encryption.

#### Point-to-site VPNs

Point-to-site VPNs allow individual client computers access to an Azure virtual network. The Secure Socket Tunneling Protocol (SSTP) creates the VPN tunnel. For more information, see Configure a point-to-site connection to a virtual network (/en-us/azure/vpn-gateway/point-to-site-certificate-gateway) .

#### Site-to-site VPNs

A site-to-site VPN gateway connection connects your on-premises network to an Azure virtual network over an IPsec/IKE VPN tunnel. For more information, see Create a site-to-site connection (/en-us/azure/vpn-gateway/tutorial-site-to-site-portal) .

## Key management with Key Vault

Without proper protection and management of keys, encryption is useless. Azure offers several key management solutions, including Azure Key Vault, Azure Key Vault Managed HSM, Azure Cloud HSM, and Azure Payment HSM.

Key Vault removes the need to configure, patch, and maintain hardware security modules (HSMs) and key management software. By using Key Vault, you maintain control—Microsoft never sees your keys, and applications don't have direct access to them. You can also import or generate keys in HSMs.

For more information about key management in Azure, see Key management in Azure (/en-us/azure/security/fundamentals/key-management) .

## Next steps

- Azure security overview (/en-us/azure/security/fundamentals/overview)
- Azure network security overview (/en-us/azure/security/fundamentals/network-overview)
- Azure database security overview (/en-us/azure/azure-sql/database/security-overview)
- Azure virtual machines security overview (/en-us/azure/security/fundamentals/virtual-machines-overview)
- Data encryption at rest (/en-us/azure/security/fundamentals/encryption-atrest)
- Data security and encryption best practices (/en-us/azure/security/fundamentals/data-encryption-best-practices)
- Key management in Azure (/en-us/azure/security/fundamentals/key-management)

## Feedback

Was this page helpful?

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

## Additional resources

- Last updated on 2026-01-16
