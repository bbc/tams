# Storage label format specification

## Abstract

Users of TAMS have requested guidance on the use of `get_url` labels on flow segments.
People want these to provide information to aid the selection of URLs where multiple are available.
This Application Note provides a specification for the format of `get_url` labels to address these needs.

In terms of requirements, we primarily want to enable the choice of get_urls based on properties such as bandwidth, latency, and cost.
Unfortunately, many of these cannot be meaningfully signalled in a direct and universal way.
If for no other reason, they are largely dependant on the intermediate infrastructure between the server and client.
This will vary based on the physical and logical location of the client as much as the server.
We must, therefore, provide enough information that the client can infer these properties themselves.
This may be done by providing information about the location, and the type of storage.

Unfortunately there is no one shared naming convention for resource locations across cloud providers.
There are shared properties (regions, and availability zones), but these aren't universally available.
Some cloud providers don't provide availability zones.
And a local installation, or one behind a CDN might not even provide regions.
So the signalling of these properties must be optional.
Availability zones may also be semi-randomised in their naming to aid in evenly distributing load across cloud infrastructure.
Zone naming is consistent within cloud accounts, though.
Co-locating within a zone can be beneficial to performance.
But this is only possible if a client knows it is within the same account as the server.
It must, then, be possible for a client to either use or ignore availability zone based on whether it is within the same cloud account.
This gives us provider, region, and availability zone as the important information that can be used to signal the location of storage.

In addition to location, storage type is important for inferring the properties of the storage.
Unfortunately, it is not possible or practical to directly compare similar types of products.
For example, cloud providers may provide Object Storage.
But they may provide multiple types of Object Storage.
These may have vastly different properties.
And there is often no universal naming conventions to describe these products in a way that is comparable between cloud providers.
So while we need to signal this, we are not able to provide universal naming conventions.

Finally, a more generic "store name" parameter is useful for human identification of stores, and for distinguishing stores which are otherwise identical.

In summary; we must signal storage provider, region, availability zone, storage type, and store name.
We cannot, unfortunately, signal any of these in consistently named and universally comparable ways.
But we can specify a schema which allows a client to consistently decide which pieces of information are important to it.

## Content

Given all of the above, this Application Note recommends the following naming convention for the `get_urls` `label` parameter on flow segments:

```text
<provider>.<region[optional]>.<availabilityZone[optional]>:<storeType>:<storeName>
```

This can be represented more formally with the following Python-compatible regex:

```regex
^(?P<provider>[A-Za-z0-9\-\_]+)(.(?P<region>[A-Za-z0-9\-\_]+)(.(?P<availabilityZone>[A-Za-z0-9\-\_]+))?)?:(?P<storeType>[A-Za-z0-9\-\_]+):(?P<storeName>[A-Za-z0-9\-\_]+)$
```

An example use of this would be:

```text
example-cloud-provider.eu-west-1.a:example-storage-product:example-store-name
```

An example use of this without an availability zone would be:

```text
example-cloud-provider.eu-west-1:example-storage-product:example-store-name
```

An example use of this without a region would be:

```text
example-cloud-provider:example-storage-product:example-store-name
```

The parameters `provider`, `region`, `availabilityZone`, and `storeType` should use the machine readable values as provided by the cloud/storage vendor.
The intention of this approach is to allow consistent values to be used without enumerating common/possible values in TAMS.

As this is an application note, this usage is a recommendation.
Not required.
This is intentional while the proposal is validated in the real world.
Once the approach has been validated, we will re-visit the possibility of moving this specification into the core API specification.

## Alternatives Considered

### URN

The [URN](https://datatracker.ietf.org/doc/html/rfc2141) format is commonly used for identifying resources.
This serves a slightly different purpose to the format described above.
The intention is to provide useful information by which available `get_urls` may be filtered.
The proposed format currently contains hierarchical location information and a human readable name.
This maps well to URNs.
As we gain more experience with this capability, we may choose to add further metadata which is not as well suited to URNs.
As such, the URN standard has not been followed.

### ARN

The [ARN](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html) format is similar to the URN format but is used exclusively by Amazon Web Services for their products.
As TAMS is intended to be agnostic to cloud providers, or indeed weather it is hosted in the cloud or not, ARNs are not a suitable option.
