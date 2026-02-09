---
status: "proposed"
---
# Signalling of timeout periods

## Context and Problem Statement

Following the creation of [ADR0043 Signalling Retention Time](../0043-signalling-retention-time.md), it was identified that there are two existing types of resource timeouts in TAMS that are not explicitly signalled.

The first is the garbage collection of Media Objects.
The spec is currently vague on how this should be implemented.
Objects are garbage collected both when they are no longer referenced by any Flow Segments, and if they are never registered against a Flow Segment.
Garbage collection where an Object is no longer referenced by a Flow Segment should happen immediately as permissions can no longer be derived from a parent Flow.
Garbage collection where an Object is never registered must happen after a period of time to allow for the opportunity for the Object to be registered against a Flow Segment.
Currently the specification only states the following:

> Service implementations need to handle situations where Objects were uploaded but no Flow Segment was registered successfully.

This means there are no explicit expectations on how much time a client has to make use of an Object.

Secondly, TAMS currently makes no recommendations on the expiry time of pre-signed URLS.
Common approaches include this information in the URL itself.
But this cannot be relied upon.
This means there are no explicit expectations on how much time a client has to make use of a pre-signed URL.

This ADR revisits both of these topics and considers potential approaches to provide explicit expectations regarding these timeouts.

## Considered Options

* Option 1a: Signal Object garbage collection timeout via the `/service` metadata
* Option 1b: Specify a fixed Object garbage collection timeout in the specification
* Option 1c: Do not specify an Object garbage collection timeout
* Option 1d: Client and Service negotiate Object garbage collection timeout
* Option 2a: Signal presigned URL expiry time via the `/service` metadata
* Option 2b: Specify presigned URL expiry time in the specification
* Option 2c: Do not specify a presigned URL expiry time
* Option 2d: Client and Service negotiate presigned URL expiry time

## Decision Outcome

Chosen option: Option 1a, and Option 2a.

These options will be implemented such that the API specification could be extended in future to support Options 1d, and 2d if required.

### Implementation

Implemented in [PR #166](https://github.com/bbc/tams/pull/166)

## Pros and Cons of the Options

### Option 1a: Signal Object garbage collection timeout via the `/service` metadata

This option would see a parameter added to the metadata at the `/service` endpoint that a Service shall use to communicate the minimum time Objects will be available for after first creation.
Clients should upload content to Objects and register them against segments within this timeframe.
The specification would include a minimum value allowing Clients to validate they meet a minimum level of performance.

* Good, because it provides a clear contract between Services and Clients regarding the timeframe in which Objects must be used
* Good, because it allows for Services to set that timeframe based on their implementation/requirements
* Good, because it provides clear performance requirements for Clients
* Bad, because it requires Clients to adapt to that signalled timeframe

### Option 1b: Specify a fixed Object garbage collection timeout in the specification

This option would see the TAMS specification specify the minimum time Objects will be available for after first creation.
Clients should upload content to Objects and register them against segments within this timeframe.

* Good, because it provides a clear contract between Services and Clients regarding the timeframe in which Objects must be used
* Good, because it doesn't require Clients to adapt to a signalled timeframe
* Bad, because it doesn't allow for Services to set that timeframe based on their implementation/requirements
* Bad, because this "minimum" would not allow Clients to rely on availability beyond the specified time, even if the Service allows use significantly beyond the specified timeframe

### Option 1c: Do not specify an Object garbage collection timeout

This option would see no changes to the TAMS specification.
The current statement in the specification - that service implementations should handle the case where Objects aren't registered - would remain.

* Good, because it allows for Services to set that timeframe based on their implementation/requirements
* Bad, because there is no clear contract between Services and Clients regarding the timeframe in which Objects must be used
* Bad, because Clients cannot adapt to this potentially variable timeframe

### Option 1d: Client and Service negotiate Object garbage collection timeout

This option would see Clients and Services actively negotiate Object garbage collection timeouts.
This would likely take the form of minimum and maximum values being advertised by the Service at it's `/service` endpoint.
Clients would then specify a value in this range when requesting Object allocation.

* Good, because it provides a clear contract between Services and Clients regarding the timeframe in which Objects must be used
* Good, because it allows for Services to set the permitted range of timeframes based on their implementation/requirements
* Good, because it allows Clients to to request a timeframe appropriate to its requirements
* Bad, because it requires Clients and Services to adapt to that negotiated timeframe
* Bad, because it adds significant complexity to the API and implementations

### Option 2a: Signal presigned URL expiry time via the `/service` metadata

This option would see a parameter added to the metadata at the `/service` endpoint that a Service shall use to communicate the minimum time pre-signed URLs will be valid for.
The specification would include a minimum value allowing Clients to validate they meet a minimum level of performance.

* Good, because it provides a clear contract between Services and Clients regarding the timeframe over which pre-signed URLs are valid.
* Good, because it allows for Services to set that timeframe based on their implementation/requirements
* Good, because it provides clear performance requirements for Clients
* Bad, because it requires Clients to adapt to that signalled timeframe

### Option 2b: Specify presigned URL expiry time in the specification

This option would see the TAMS specification specify the minimum time pre-signed URLs will be valid for.

* Good, because it provides a clear contract between Services and Clients regarding the timeframe over which pre-signed URLs are valid.
* Good, because it doesn't require Clients to adapt to a signalled timeframe
* Bad, because it doesn't allow for Services to set that timeframe based on their implementation/requirements
* Bad, because this "minimum" would not allow Clients to rely on availability beyond the specified time, even if the Service allows use significantly beyond the specified timeframe

### Option 2c: Do not specify a presigned URL expiry time

This option would see no changes to the TAMS specification.

* Good, because it allows for Services to set that timeframe based on their implementation/requirements
* Bad, because there is no clear contract between Services and Clients regarding the timeframe over which pre-signed URLs are valid
* Bad, because Clients cannot adapt to this potentially variable timeframe

### Option 2d: Client and Service negotiate presigned URL expiry time

This option would see Clients and Services actively negotiate the time pre-signed URLs will be valid for.
This would likely take the form of minimum and maximum values being advertised by the Service at it's `/service` endpoint.
Clients would then specify a value in this range when requesting pre-signed URLs.

* Good, because it provides a clear contract between Services and Clients regarding the timeframe over which pre-signed URLs are valid.
* Good, because it allows for Services to set the permitted range of timeframes based on their implementation/requirements
* Good, because it allows Clients to to request a timeframe appropriate to its requirements
* Bad, because it requires Clients and Services to adapt to that negotiated timeframe
* Bad, because it adds significant complexity to the API and implementations
