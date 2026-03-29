# GCP VPC

Source pages:
- Virtual Private Cloud (VPC) overview: https://cloud.google.com/vpc/docs/overview
- Firewall policies and rules: https://cloud.google.com/vpc/docs/firewall-policies-overview

## Virtual Private Cloud (VPC) overview

Source: https://cloud.google.com/vpc/docs/overview

# Virtual Private Cloud (VPC) overview

Virtual Private Cloud (VPC) provides networking functionality to Compute Engine virtual machine (VM) instances (/compute/docs/instances) , Google Kubernetes Engine (GKE) clusters (/kubernetes-engine/docs) , and serverless workloads (/serverless#section-3) .

VPC provides networking for your cloud-based resources and services that is global, scalable, and flexible.

This page provides a high-level overview of VPC concepts and features.

## VPC networks

You can think of a VPC network the same way you'd think of a physical network, except that it is virtualized within Google Cloud. A VPC network is a global resource that consists of a list of regional virtual subnetworks (subnets) in data centers, all connected by a global wide area network. VPC networks are logically isolated from each other in Google Cloud.
VPC network example (click to enlarge).

A VPC network does the following:

- Provides connectivity for your Compute Engine virtual machine (VM) instances (/compute/docs/instances) , including Google Kubernetes Engine (GKE) clusters (/kubernetes-engine/docs/concepts/cluster-architecture) , serverless workloads (/serverless#section-3) , and other Google Cloud products built on Compute Engine VMs.
- Offers built-in internal passthrough Network Load Balancers and proxy systems for internal Application Load Balancers.
- Connects to on-premises networks by using Cloud VPN tunnels and VLAN attachments for Cloud Interconnect.
- Distributes traffic from Google Cloud external load balancers to backends.

For more information, see VPC networks (/vpc/docs/vpc) .

### Firewall rules

Each VPC network implements a distributed virtual firewall that you can configure. Firewall rules let you control which packets are allowed to travel to which destinations. Every VPC network has two implied firewall rules (/vpc/docs/firewalls#default_firewall_rules) that block all incoming connections and allow all outgoing connections.
The`default`network has additional firewall rules (/vpc/docs/firewalls#more_rules_default_vpc) , including the`default-allow-internal`rule, which permit communication among instances in the network.

For more information, see VPC firewall rules (/vpc/docs/firewalls) .

### Routes

Routes tell VM instances and the VPC network how to send traffic from an instance to a destination, either inside the network or outside of Google Cloud. Each VPC network comes with some system-generated routes (/vpc/docs/vpc#system-generated-routes) to route traffic among its subnets and send traffic from eligible instances (/vpc/docs/vpc#internet_access_reqs) to the internet.

You can create custom static routes to direct some packets to specific destinations.

For more information, see Routes (/vpc/docs/routes) .

### Forwarding rules

While routes govern traffic leaving an instance, forwarding rules direct traffic to a Google Cloud resource in a VPC network based on IP address, protocol, and port.

Some forwarding rules direct traffic from outside of Google Cloud to a destination in the network; others direct traffic from inside the network. Destinations for forwarding rules are target instances (/load-balancing/docs/protocol-forwarding) , load balancer targets (backend services, target proxies, and target pools) (/load-balancing/docs/forwarding-rule-concepts) , and Classic VPN gateways (/network-connectivity/docs/vpn/concepts/classic-topologies) .

For more information, see Forwarding rules overview (/load-balancing/docs/forwarding-rule-concepts) .

## Interfaces and IP addresses

VPC networks provide the following configurations for IP addresses and VM network interfaces.

### IP addresses

Google Cloud resources, such as Compute Engine VM instances, forwarding rules, and GKE containers, rely on IP addresses to communicate.

For more information, see IP addresses (/vpc/docs/ip-addresses) .

### Alias IP ranges

If you have multiple services running on a single VM instance, you can give each service a different internal IP address by using alias IP ranges. The VPC network forwards packets that are destined to a particular service to the corresponding VM.

For more information, see Alias IP ranges (/vpc/docs/alias-ip) .

### Multiple network interfaces

You can add multiple network interfaces to a VM instance. Multiple network interfaces enable use cases such as using a network appliance VM to act as a gateway for securing traffic among different VPC networks or to and from the internet.

For more information, see Multiple network interfaces (/vpc/docs/multiple-interfaces-concepts) .

## VPC sharing and peering

Google Cloud provides the following configurations for sharing VPC networks across projects and connecting VPC networks to each other.

### Network Connectivity Center

You can use Network Connectivity Center (NCC) to connect VPC networks by using a hub and spoke connectivity model. VPC spokes let you connect two or more VPC networks to an NCC hub so that the networks exchange subnet routes (/vpc/docs/routes#subnet-routes) . You can connect and manage hundreds of VPC spokes from a single hub.

For more information, see NCC overview (/network-connectivity/docs/network-connectivity-center/concepts/overview) .

### VPC Network Peering

VPC Network Peering lets you build software as a service (SaaS) (https://wikipedia.org/wiki/Software_as_a_service) ecosystems in Google Cloud, making services available privately across different VPC networks, whether the networks are in the same project, different projects, or projects in different organizations.

With VPC Network Peering, all communication happens by using internal IP addresses. Subject to firewall rules, VM instances in each peered network can communicate with one another without using external IP addresses.

Peered networks automatically exchange subnet routes for private IP address ranges. VPC Network Peering lets you configure whether the following types of routes are exchanged:

- Subnet routes for privately re-used public IP ranges
- Custom static and dynamic routes

Network administration for each peered network is unchanged: IAM policies are never exchanged by VPC Network Peering. For example, Network and Security Admins for one VPC network don't automatically get those roles for the peered network.

For more information, see VPC Network Peering (/vpc/docs/vpc-peering) .

### Shared VPC

You can share a VPC network from one project (called a host project) to other projects in your Google Cloud organization. You can grant access to entire Shared VPC networks or select subnets therein by using specific IAM permissions (/vpc/docs/shared-vpc#iam_in_shared_vpc) . This lets you provide centralized control over a common network while maintaining organizational flexibility. Shared VPC is especially useful in large organizations.

For more information, see Shared VPC (/vpc/docs/shared-vpc) .

## Hybrid cloud

Google Cloud provides the following configurations that let you connect your VPC networks to on-premises networks and networks from other cloud providers.

### Cloud VPN

Cloud VPN lets you connect your VPC network to your physical, on-premises network or another cloud provider by using a secure virtual private network (https://wikipedia.org/wiki/Virtual_private_network) .

For more information, see Cloud VPN (/network-connectivity/docs/vpn) .

### Cloud Interconnect

Cloud Interconnect lets you connect your VPC network to your on-premises network by using a high speed physical connection.

For more information, see Cloud Interconnect (/network-connectivity/docs/interconnect) .

### Hybrid Subnets

Hybrid Subnets helps you migrate workloads to Google Cloud without needing to change any IP addresses. A hybrid subnet is a single logical subnet that combines a segment of an on-premises network with a subnet in a VPC network.

For more information, see Hybrid Subnets (/vpc/docs/hybrid-subnets) .

## Cloud Load Balancing

Google Cloud offers several load balancing configurations to distribute traffic and workloads across many backend types.

For more information, see Cloud Load Balancing overview (/load-balancing/docs/load-balancing-overview) .

## Private access to services

You can use Private Service Connect (/vpc/docs/private-service-connect) and Private Google Access (/vpc/docs/private-google-access) , and private services access (/vpc/docs/private-services-access) to let VMs that don't have an external IP address communicate with supported services.

For more information, see Private access options for services (/vpc/docs/private-access-options) .

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/) , and code samples are licensed under the Apache 2.0 License (https://www.apache.org/licenses/LICENSE-2.0) . For details, see the Google Developers Site Policies (https://developers.google.com/site-policies) . Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.


## Firewall policies and rules

Source: https://cloud.google.com/vpc/docs/firewall-policies-overview

# Firewall policies and rules

A firewall rule in Cloud Next Generation Firewall determines whether to allow or deny traffic within a Virtual Private Cloud (VPC) network based on defined criteria. A Cloud NGFW firewall policy lets you group several firewall rules so that you can update them all at once, effectively controlled by Identity and Access Management (IAM) roles.

This document provides an overview of the different types of firewall policies and firewall policy rules.

## Firewall policies

Cloud NGFW supports the following types of firewall policies:

- Hierarchical firewall policies (#hierarchical_firewall_policies)
- Global network firewall policies (#global_network_firewall_policies)
- Regional network firewall policies (#regional_network_firewall_policies)
- Regional system firewall policies (#regional-system-firewall-policies)

### Hierarchical firewall policies

Hierarchical firewall policies let you group rules into a policy object that can apply to many VPC networks in one or more projects. You can associate hierarchical firewall policies with an entire organization (/resource-manager/docs/cloud-platform-resource-hierarchy#organizations) or individual folders (/resource-manager/docs/cloud-platform-resource-hierarchy#folders) .

For hierarchical firewall policy specifications and details, see Hierarchical firewall policies (/firewall/docs/firewall-policies) .

### Global network firewall policies

Global network firewall policies let you group rules into a policy object that can apply to all regions of a VPC network.

For global network firewall policy specifications and details, see Global network firewall policies (/firewall/docs/network-firewall-policies) .

### Regional network firewall policies

Regional network firewall policies let you group rules into a policy object that can apply to a specific region of a VPC network.

For regional firewall policy specifications and details, see Regional network firewall policies (/firewall/docs/regional-firewall-policies) .

### Regional system firewall policies

Regional system firewall policies are similar to regional network firewall policies, but they are managed by Google. Regional system firewall policies have the following characteristics:

Google Cloud evaluates rules in regional system firewall policies immediately after evaluating rules in hierarchical firewall policies. For more information, see Firewall rule evaluation process (/firewall/docs/firewall-policies-rule-eval-order) .

You can't modify a rule in a regional system firewall policy, except to enable or disable firewall rule logging.

Google Cloud creates a regional system firewall policy in a region of a VPC network when a Google service requires rules in that region of the network. Google Cloud can associate more than one regional system firewall policy with a region of a VPC network based on the requirements of Google services.

You aren't charged for the evaluation of rules in regional system firewall policies.

## Network profile interaction

Regular VPC networks support firewall rules in hierarchical firewall policies, global network firewall policies, regional network firewall policies, and VPC firewall rules. All firewall rules are programmed as part of the Andromeda network virtualization stack (https://www.usenix.org/system/files/conference/nsdi18/nsdi18-dalton.pdf) .

VPC networks that use certain network profiles (/vpc/docs/network-profiles) restrict the firewall policies and rule attributes that you can use. For RoCE VPC networks, see Cloud NGFW for RoCE VPC networks (/firewall/docs/firewall-for-roce) instead of this page.

## Firewall policy rules

In Google Cloud, a firewall policy rule has a direction that determines whether it controls traffic coming into your network or traffic leaving it. Each firewall policy rule applies to either incoming (ingress) or outgoing (egress) connections.

### Ingress rules

Ingress direction refers to the incoming connections sent from specific sources to Google Cloud targets. Ingress rules apply to inbound packets that arrive on the following types of targets:

- Network interfaces of virtual machine (VM) instances
- Managed Envoy proxies that power internal Application Load Balancers and internal proxy Network Load Balancers

An ingress rule with a`deny`action protects targets by blocking incoming connections to them. If a rule with a higher priority allows traffic, the firewall permits it and ignores any lower priority rules that might deny that same traffic. Remember, higher priority rules always take precedence.

An automatically created default network includes some pre-populated VPC firewall rules (/firewall/docs/firewalls#more_rules_default_vpc) , which allow ingress for certain types of traffic.

### Egress rules

Egress direction refers to the outbound traffic sent from a target Google Cloud resource, such as a VM network interface, to a destination.

An egress rule with an`allow`action lets an instance send traffic to the destinations specified in the rule. Egress traffic is blocked if it matches a high priority`deny`rule. This action takes precedence over any lower priority rules that might allow the traffic. Google Cloud also blocks or limits (/firewall/docs/firewalls#blockedtraffic) certain kinds of traffic.

## What's next

- To create and modify hierarchical firewall policies and rules, see Use hierarchical firewall policies and rules (/firewall/docs/using-firewall-policies) .
- To create and modify global network firewall policies and rules, see Use global network firewall policies and rules (/firewall/docs/use-network-firewall-policies) .
- To create and modify regional network firewall policies and rules, see Use regional network firewall policies and rules (/firewall/docs/use-regional-firewall-policies) .

Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License (https://creativecommons.org/licenses/by/4.0/) , and code samples are licensed under the Apache 2.0 License (https://www.apache.org/licenses/LICENSE-2.0) . For details, see the Google Developers Site Policies (https://developers.google.com/site-policies) . Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2026-03-26 UTC.
