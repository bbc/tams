#!/usr/bin/env python
# This script demonstrates ingest of media from an HLS playlist into TAMS

import json
from typing import Generator, Any, AsyncGenerator, Optional
import asyncio
import os
import logging
from argparse import ArgumentParser
from uuid import UUID, uuid4

import aiohttp
import m3u8
from mediatimestamp import TimeRange, Timestamp
import mediajson
import av

from credentials import Credentials, BasicCredentials, OAuth2ClientCredentials
from client import post_request, put_request

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEFAULT_FLOW_METADATA = {
    "label": "Demo Flow",
    "description": "Flow created to demonstrate manual upload",
    "format": "urn:x-nmos:format:video",
    "codec": "video/h264",
    "container": "video/mp2t",
    "essence_parameters": {
        "frame_rate": {
            "numerator": 50,
            "denominator": 1
        },
        "frame_width": 1920,
        "frame_height": 1080,
        "bit_depth": 8,
        "interlace_mode": "progressive",
        "component_type": "YCbCr",
        "horiz_chroma_subs": 2,
        "vert_chroma_subs": 2
    }
}


async def put_flow(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    tams_url: str,
    flow_id: UUID,
    source_id: UUID,
    flow_metadata: Optional[dict]
) -> None:
    """Create a H.264 video Flow (note: the given `flow_metadata` will be mutated)"""
    if flow_metadata is None:
        flow_metadata = DEFAULT_FLOW_METADATA

    flow_metadata["id"] = str(flow_id)
    flow_metadata["source_id"] = str(source_id)

    logger.info(f"Creating Flow {flow_id}")

    async with put_request(
        session,
        credentials,
        f"{tams_url}/flows/{flow_id}",
        json=flow_metadata
    ) as resp:
        resp.raise_for_status()


async def get_media_storage_urls(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    tams_url: str,
    flow_id: UUID,
    segment_count: int
) -> AsyncGenerator[dict, None]:
    """Get media storage URLs for uploading media segments"""
    while True:
        async with post_request(
            session,
            credentials,
            f"{tams_url}/flows/{flow_id}/storage",
            json={
                "limit": segment_count
            }
        ) as resp:
            resp.raise_for_status()

            media_storage = await resp.json()
            media_object_urls = media_storage["media_objects"]

            for object_url in media_object_urls:
                yield object_url


def get_hls_segment_filenames(hls_filename: str) -> Generator[str, None, None]:
    """Return list of segment filenames from the playlist"""
    playlist = m3u8.load(hls_filename)

    for segment in playlist.segments:
        yield segment.uri


def extract_segment_timerange(filename: str) -> TimeRange:
    """Extract the presentation timerange from the media object

    This implementation is very basic. It could be optimised further to avoid
    reading and parsing the complete segment.

    This implementation assumes that the packet durations are known. This
    allows the segment timerange to include the last frame's duration with an
    exclusive end timestamp.

    The start_time and duration attributes of `input` could also be used but
    would result in some timestamp value truncation for common frame rates
    because they only have a microsecond resolution. The TimeRange.normalise
    method could be used if the input timestamps are equivalent to frame counts.

    This implementation does not account for timestamp rollover in the MPEG-TS
    container or wallclock timing, which would require use of the
    FlowSegment.ts_offset property to position the segment on the Flow timeline.
    """
    start_ts = None
    end_ts = None
    end_duration = None
    with av.open(filename, "r") as input:
        for pkt in input.demux():
            if pkt.pts is None:
                continue

            ts = Timestamp.from_count(pkt.pts, 1/pkt.time_base)
            duration = Timestamp.from_count(pkt.duration, 1/pkt.time_base)

            if start_ts is None:
                start_ts = ts
                end_ts = ts
                end_duration = duration
            else:
                start_ts = min(ts, start_ts)
                end_ts = max(ts, end_ts)
                if ts == end_ts:
                    end_duration = duration

    return TimeRange(start_ts, end_ts + end_duration, TimeRange.INCLUDE_START)


async def ingest_segment(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    tams_url: str,
    flow_id: UUID,
    object_url: dict[str, Any],
    filename: str
) -> None:
    """Upload the segment's media object and register the segment"""
    seg_tr = await asyncio.get_running_loop().run_in_executor(
        None,
        extract_segment_timerange,
        filename
    )

    first_object_url = object_url["put_url"]["url"]
    content_type = object_url["put_url"]["content-type"]
    with open(filename, "rb") as f:
        async with session.put(
            first_object_url,
            data=f,
            headers={
                "Content-Type": content_type
            }
        ) as resp:
            resp.raise_for_status()

    logger.info(f"Uploaded object to {object_url['object_id']}")

    async with post_request(
        session,
        credentials,
        f"{tams_url}/flows/{flow_id}/segments",
        json=mediajson.encode_value({
            "object_id": object_url['object_id'],
            "timerange": seg_tr
        })
    ) as resp:
        resp.raise_for_status()

    logger.info(f"Created flow segment for {object_url['object_id']} at {seg_tr.to_sec_nsec_range()}")


async def hls_ingest(
    tams_url: str,
    credentials: Credentials,
    hls_filename: str,
    hls_start_segment: int,
    hls_segment_count: int,
    flow_id: UUID,
    source_id: UUID,
    flow_params: Optional[dict]
) -> None:
    """Upload segments from the HLS playlist"""
    async with aiohttp.ClientSession() as session:
        await put_flow(session, credentials, tams_url, flow_id, source_id, flow_params)

        object_urls = get_media_storage_urls(session, credentials, tams_url, flow_id, hls_segment_count)

        hls_segment_filenames = get_hls_segment_filenames(hls_filename)

        # This sequential upload process could be optimised by using asyncio tasks to
        # ingest segments concurrently
        count = 0
        for segment_filename in hls_segment_filenames:
            count += 1
            if count <= hls_start_segment:
                continue
            elif count > hls_start_segment + hls_segment_count:
                break

            object_url = await anext(object_urls)

            full_segment_filename = os.path.join(os.path.dirname(hls_filename), segment_filename)

            await ingest_segment(
                session,
                credentials,
                tams_url,
                flow_id,
                object_url,
                full_segment_filename
            )


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="ingest_hls",
        description="TAMS Flow ingest from HLS basic example"
    )

    parser.add_argument(
        "--tams-url", type=str, required=True,
        help=("URL of the top level endpoint in the TAMS service. "
              "For Squirrel this must include the '/x-cloudfit/squirrelmediastore/<version>' path")
    )
    parser.add_argument(
        "--oauth2-url", type=str, default=os.environ.get("OAUTH2_URL"),
        help="OAuth2 URL for getting credential token. Defaults to the 'OAUTH2_URL' environment variable"
    )
    parser.add_argument(
        "--client-id", type=str, default=os.environ.get("CLIENT_ID"),
        help="Keycloak client secret. Defaults to the 'CLIENT_ID' environment variable"
    )
    parser.add_argument(
        "--client-secret", type=str, default=os.environ.get("CLIENT_SECRET"),
        help="Keycloak client secret. Defaults to the 'CLIENT_SECRET' environment variable"
    )
    parser.add_argument(
        "--username", type=str, default=os.environ.get("USERNAME"),
        help="Basic auth username. Defaults to the 'USERNAME' environment variable"
    )
    parser.add_argument(
        "--password", type=str, default=os.environ.get("PASSWORD"),
        help="Basic auth password. Defaults to the 'PASSWORD' environment variable"
    )
    parser.add_argument(
        "--hls-filename", type=str, default="sample_content/hls_output.m3u8",
        help="HLS playlist providing segment files"
    )
    parser.add_argument(
        "--hls-start-segment", type=int, default=0,
        help="Segment number to start ingesting from"
    )
    parser.add_argument(
        "--hls-segment-count", type=int, default=30,
        help="Maximum number of segments to ingest"
    )
    parser.add_argument(
        "--flow-id", type=UUID,
        help="Flow ID for the sample content. Default is to generate an ID"
    )
    parser.add_argument(
        "--source-id", type=UUID,
        help="Source ID for the sample content. Default is to generate an ID"
    )
    parser.add_argument(
        "--flow-params", type=json.loads,
        help="JSON representation of Flow to write. Default is a basic video Flow"
    )

    args = parser.parse_args()

    credentials: Credentials
    if args.oauth2_url and args.client_id and args.client_secret:
        credentials = OAuth2ClientCredentials(args.oauth2_url, args.client_id, args.client_secret)
    elif args.username and args.password:
        credentials = BasicCredentials(args.username, args.password)
    else:
        logger.error(
            "Require either OAuth2 credentials (--oauth2-url, --client-id, --client-secret) "
            "or basic credentials (--username, --password)"
        )

    output_timerange = asyncio.run(hls_ingest(
        args.tams_url.rstrip("/"),
        credentials,
        args.hls_filename,
        args.hls_start_segment,
        args.hls_segment_count,
        args.flow_id or uuid4(),
        args.source_id or uuid4(),
        args.flow_params
    ))
