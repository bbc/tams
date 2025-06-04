# 0009: Storage label format specification

> [!CAUTION]
> DEPRECATED: See [ADR0032](https://github.com/bbc/tams/blob/main/docs/appnotes/0032-specifying-storage-location.md) for more details

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
Some cloud providers don't provide availability zones, or have services that run at a regional level so don't need the availability zone to be specified.
And a local installation, or one behind a CDN might not even provide regions.
So the signalling of these properties must be optional.
Availability zones may also be semi-randomised in their naming to aid in evenly distributing load across cloud infrastructure.
Zone naming is consistent within cloud accounts, though.
Cloud providers may also provide zone IDs which are consistent between accounts as an alternative.
Co-locating within a zone can be beneficial to performance.
But this is only possible if a client knows it is within the same physical zone as the server.
It must, then, be possible for a client to either use or ignore availability zone based on whether it can be certain it is co-located physically.
This gives us provider, region, and availability zone as the important information that can be used to signal the location of storage.

In addition to location, storage type is important for inferring the properties of the storage.
Unfortunately, it is not possible or practical to directly compare similar types of products.
For example, cloud providers may provide Object Storage.
But they may provide multiple types of Object Storage.
These may have vastly different properties.
And there is often no universal naming conventions to describe these products in a way that is comparable between cloud providers.
So while we need to signal this, we are not able to provide universal naming conventions.
The storage type can optionally indicate whether the URLs are presigned or not.

Finally, a more generic "store name" parameter is useful for human identification of stores, and for distinguishing stores which are otherwise identical.
It should be noted that the logical concept of a named "store" in this case is distinct from a bucket (or equivalent concept).
A "store" may make use of multiple buckets for performance reasons, for example.
But the properties of buckets of a named store should be otherwise identical.

In summary; we must signal storage provider, storage type, and store name.
However we may also need to add the optional parameters of region, and availability zone.
We cannot, unfortunately, signal any of these in consistently named and universally comparable ways.
But we can specify a schema which allows a client to consistently decide which pieces of information are important to it.

## Content

Given all of the above, this Application Note recommends the following naming convention for the `get_urls` `label` parameter on flow segments:

```text
<provider>.<region[optional]>.<availabilityZone[optional]>:<storeType>.<presigned[optional]>:<storeName>
```

This can be represented more formally with the following Python-compatible regex:

```regex
^(?P<provider>[A-Za-z0-9\-\_]+)(\.(?P<region>[A-Za-z0-9\-\_]+)(\.(?P<availabilityZone>[A-Za-z0-9\-\_]+))?)?:(?P<storeType>[A-Za-z0-9\-\_]+)(\.presigned)?:(?P<storeName>[A-Za-z0-9\-\_]+)$
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

An example use of this with presigned URLs would be:

```text
example-cloud-provider.eu-west-1.a:example-storage-product.presigned:example-store-name
```

The parameters `provider`, `region`, `availabilityZone`, and `storeType` should use the machine readable values as provided by the cloud/storage vendor.
Where multiple case variants exist for parameters (i.e. upper/lower/mixed case), lower case should be preferred.
The intention of this approach is to allow consistent values to be used without enumerating common/possible values in TAMS.

For `availabilityZone` - where a cloud provider provides an identifier which is consistent between accounts, this should be favoured over semi-randomised identifiers (e.g. prefer availability zone IDs over availability zone Names on AWS).

As this is an application note, this usage is a recommendation.
Not required.
This is intentional while the proposal is validated in the real world.
Once the approach has been validated, we will re-visit the possibility of moving this specification into the core API specification.

### Example mappings

#### AWS S3

For this AWS S3 ARN:

```text
arn:aws:s3:::example-bucket-name
```

You may use the following label:

```text
aws.eu-west-1:s3:example-store-name
```

Note: S3 **is** region specific, but does not include the region in the ARN.
Standard S3 is NOT availability zone specific.
The `storeName` does not need to match the bucket name, but you may decide it would be sensible for a given implementation to do so.

#### AWS S3 Express One Zone

For this AWS S3 Express One Zone ARN:

```text
arn:aws:s3express:us-west-2:123456789012:bucket/example-bucket-name-express--usw2-az1--x-s3
```

You may use the following label:

```text
aws.us-west-2.usw2-az1:s3express:example-store-name
```

Note: S3 Express One Zone buckets are attached to a single availability zone.
ARNs, and other machine readable/configuration locations in AWS commonly identify availability zones with a Name, which is consistent within an account but not between accounts.
AWS also provide availability zone IDs that are consistent between accounts, but are less commonly used.
Use of the availability zone ID is recommended due to this cross-account consistency.
The availability zone ID is always embedded in the bucket name in the ARN for S3 Express.
The `storeName` does not need to match the bucket name, but you may decide it would be sensible for a given implementation to do so.

#### Azure Blobs

For this Azure Blob URN:

```text
https://myaccount.blob.core.windows.net/example-container-name
```

You may use the following label:

```text
windows.uksouth:blob:example-store-name
```

Note: Blobs **is** region specific, but does not include the region in the URN (some other services do include the ARN).
The `storeName` does not need to match the container name, but you may decide it would be sensible for a given implementation to do so.

#### Google Cloud Storage

For this Google Cloud full resource name:

```text
//storage.googleapis.com/projects/_/buckets/example-bucket-name
```

You may use the following label:

```text
google.europe-west2:storage:example-store-name
```

Note: Google Cloud Storage **is** region specific, but does not include the region in the URN (some other services do include the ARN).
The `storeName` does not need to match the container name, but you may decide it would be sensible for a given implementation to do so.
In this case, the URL is a long form `googleapis`.
This has been shortened in this example to just the company name.

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
