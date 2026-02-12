# TAMS Examples

This directory contains a number of Python scripts that demonstrate some basic uses of the TAMS API.

## Prerequisites

The following is required to run the example scripts:

* A TAMS store (e.g. deploying the [AWS Labs Time-addressable Media Store](https://github.com/awslabs/time-addressable-media-store) or similar)
  * the API URL is passed to the scripts using the `--tams-url` arg
  * the scripts assume that media objects can be read and written using pre-signed URLs
* API credentials, either
  * OAuth2 Client Credentials Grant passed in using `--oauth2-url`, `--client-id` and `--client-secret` commandline args or provided via `OAUTH2_URL`, `CLIENT_ID` and `CLIENT_SECRET` environment variables
  * basic username / password credentials, passed in using `--username` and `--password` commandline args or provided via `USERNAME` and `PASSWORD` environment variables
* Python
* curl, to download the Big Bug Bunny sample content
* FFmpeg, for creating the sample HLS content for ingest

## Running Examples

### Sample Content

The [Big Buck Bunny](https://peach.blender.org/) short film is used as sample content for ingesting into TAMS.
Run `make sample_content` to download a file containing 30 fps HD and convert it to a video-only HLS playlist using ffmpeg.
The result can be found in the `sample_content/` folder.

### Virtual Environment

The scripts can be run in a virtual environment.
Run `make venv` to create a virtual environment and install the [requirements](./requirements.txt).
Run `. venv/bin/activate` to activate the virtual environment.

### API Credentials

The scripts require TAMS API credentials and these can also be provided as environment variables rather than as commandline args.
Run `make env_exports` to get a list of the exports that can be used (see [Prerequisites](#prerequisites)).

### Environment and Commandline Args

Run the scripts using `python <script>` or just `./<script>` to get help on the available args.

E.g., to run a script with OAuth2 credentials you can

* set the credentials using environment variables.
E.g.

```bash
export OAUTH2_URL=https://demo-oauth2-service.example.com/token
export CLIENT_ID=demo
export CLIENT_SECRET=asecret
```

* and then run the script with the `--tams-url` arg to set the TAMS API URL and as well as any other args.
E.g.

```bash
./outgest_file.py --tams-url https://tams-service.example.com --flow-id eca3c5ff-d5b0-44b7-bd17-e58863f69bed --check-timing --output output.ts
```


## Examples

### TAMS API Client Access ([client.py](./client.py) and [credentials.py](./credentials.py))

The [credentials.py](./credentials.py) script provides classes for basic authentication and OAuth2 Client Credentials Grant authentication.

> There may be other forms of authentication supported by a TAMS instance.

The [client.py](./client.py) script provides context managers for making HTTP API requests using [aiohttp](https://docs.aiohttp.org/en/stable/).
It includes a simple retry mechanism in case the OAuth2 credentials have expired.

> A more complete implementation of a TAMS `client` would provide methods for each endpoint as well as higher level functionality.
It would also handle other temporary API failures that can be expected in cloud-based systems using some form of exponential retry.

### Ingest HLS ([ingest_hls.py](./ingest_hls.py))

The [ingest_hls.py](./ingest_hls.py) script demonstrates how already segmented content from an HLS playlist can easily be ingested into TAMS.

The script makes some assumptions about the media content (e.g. the resulting Flow properties) and therefore it is best to use the [sample content](#sample-content).

Run the script as follows (replace `<URL>`),

```bash
./ingest_hls.py --tams-url <URL> --hls-filename sample_content/hls_output.m3u8
```

The output Flow ID is logged as well as each segment timerange that is ingested from the HLS playlist.

By default at most 30 segments will be ingested.

The script follows these steps:

* a new Flow is created with (hardcoded) properties that match the sample content
* the segment filenames are extracted from the playlist `sample_content/hls_output.m3u8`
* each segment media file is read to extract the timerange
* each segment media file is uploaded using the pre-signed URLs provided by the TAMS
* each segment is registered in TAMS

The script also has args to

* change the start segment (`--hls-start-segment`) and number of segments (`--hls-segment-count`) limit, i.e. override the default 30 segment limit
* set the Flow ID (`--flow-id`) and Source ID (`--source-id`)

> The timerange extraction process as implemented is not optimal in terms of speed (e.g. it doesn't need to read all the frames) but at least it is more accurate than using the segment durations from the HLS playlist.
>
> The Big Buck Bunny sample file has a presentation start time of 0.066666 (6000/90000) seconds, which is why the first segment's timerange (`[0:66666666_8:399999999)`) is offset from 0.
>
> The script makes no assumption about whether the timestamps in the MPEG-TS are equivalent to frame counts or not.
This is why the exclusive end of the first segment is left as `8:399999999`.
If the timing is known to be 30 Hz (which it is for this sample content) then the end could've been normalised to `8:400000000` using the `TimeRange` [normalise](https://bbc.github.io/rd-apmm-python-lib-mediatimestamp/mediatimestamp/mediatimestamp.html#TimeRange.normalise) method.
>
> The script has not been optimised to upload segments concurrently.

### Outgest File ([outgest_file.py](./outgest_file.py))

The [outgest_file.py](./ingest_hls.py) script demonstrates how Flow media can be exported to a local file.

Run the script as follows (replace `<URL>` and set `<FLOW ID>` to the Flow ID logged by the [ingest HLS script](#ingest-hls-ingest_hlspy)),

```bash
./outgest_file.py --tams-url <URL> --flow-id <FLOW ID> --check-timing --output output.ts
```

The script logs the segments that are being downloaded and re-wrapped into the local MPEG-TS file, `output.ts`.

The `--check-timing` arg enables some timing validation of the segments and warns if the segment timerange does not match the media file timerange (taking segment time offsets (`ts_offset`) into account).

The script also has a `--timerange` arg to limit the timerange outgested.

The script follows these steps:

* a local MPEG-TS file is opened
* segments are requested for the given Flow and timerange
* each segment media object is downloaded using a TAMS provided pre-signed URL
* the media timing is adjusted using the segment `ts_offset`, `sample_offset` and `sample_count` properties as required as well as timestamp rollover within the segment time period
* the media is re-wrapped to the local MPEG-TS file

> The script has not been optimised to download segments concurrently.

### Simple Edit ([simple_edit.py](./simple_edit.py))

The [simple_edit.py](./ingest_hls.py) script demonstrates how media can be shared between Flows using a lightweight metadata-only operation that constructs a Flow from timeranges of other Flows.
The script takes 2 Flows and timeranges as inputs, and creates an output Flow that is a concatenation of the 2 inputs, containing at most one page of segments from each.

Firstly, create the 2 input Flows from the sample content.

Run the [ingest HLS](#ingest-hls-ingest_hlspy) script as follows (replace `<URL>`),

```bash
./ingest_hls.py --tams-url <URL> --hls-filename sample_content/hls_output.m3u8 --hls-start-segment 0 --hls-segment-count 5
```

This will create Flow 1 that contains 5 segments of the sample content at the start.

Run the [ingest HLS](#ingest-hls-ingest_hlspy) script again as follows (replace `<URL>`),

```bash
./ingest_hls.py --tams-url <URL> --hls-filename sample_content/hls_output.m3u8 --hls-start-segment 5 --hls-segment-count 5
```

This will create Flow 2 that contains 5 segments of sample content starting from the 5th segment.

Finally, run the simple edit script to create a Flow from the 2 Flows in reverse time order (replace `<URL>` and set `<FLOW ID 2>` and `<FLOW ID 1>` to the Flow IDs logged previously),

```bash
./simple_edit.py --tams-url <URL> --input1-flow-id <FLOW ID 2> --input2-flow-id <FLOW ID 1>
```

Run the outgest file script as follows (replace `<URL>` and set `<FLOW ID>` to the Flow ID logged by the simple edit script),

```bash
./outgest_file.py --tams-url <URL> --flow-id <FLOW ID> --check-timing --output output.ts
```

The simple edit example has another mode as well, to demonstrate the `sample_offset` and `sample_count` segment
properties used to set edit points within segments.
This mode can be used by adding the `--cut-interval-sec <seconds>` parameter to the `./simple_edit.py` command, and
will cut between the two Flows on that interval.
The resulting Flow will not be playable using simple tools (such as direct HLS mappings) and will require a client that
fully implements the TAMS specification, including handling long-GOP precharge if necessary.

### Authorization Proxy ([authz_proxy](./authz_proxy))

This [authorization proxy](./authz_proxy) demonstrates Fine-Grained Authorisation (FGA) using a reverse proxy in front of a TAMS API instance, by matching user group membership to an `auth_classes` tag on Sources, Flows and Webhooks.
