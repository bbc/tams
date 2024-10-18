#!/usr/bin/env python
# This script demonstrates a simple edit of 2 Flows using segment metadata only

import asyncio
import os
import logging
from argparse import ArgumentParser
from uuid import UUID, uuid4
from fractions import Fraction

import aiohttp
from mediatimestamp import TimeRange, Timestamp
import mediajson

from credentials import Credentials, BasicCredentials, OAuth2ClientCredentials
from client import post_request, put_request, get_request

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def put_flow(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    tams_url: str,
    flow_id: UUID,
    source_id: UUID
) -> None:
    """Create a new H.264 video Flow which should match input 1 and input 2"""
    flow_metadata = {
        "id": str(flow_id),
        "source_id": str(source_id),
        "label": "Copy Edit Flow",
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

    logger.info(f"Creating Flow {flow_id}")

    async with put_request(
        session,
        credentials,
        f"{tams_url}/flows/{flow_id}",
        json=flow_metadata
    ) as resp:
        resp.raise_for_status()


async def simple_edit(
    tams_url: str,
    credentials: Credentials,
    input_1_flow_id: UUID,
    input_1_timerange: TimeRange,
    input_2_flow_id: UUID,
    input_2_timerange: TimeRange,
    output_flow_id: UUID,
    output_source_id: UUID
) -> None:
    """Add timerange of segments from input 1 followed by a timerange of segments from input 2"""
    async with aiohttp.ClientSession() as session:
        await put_flow(session, credentials, tams_url, output_flow_id, output_source_id)

        # Add segments from input 1 to output
        async with get_request(
            session,
            credentials,
            f"{tams_url}/flows/{input_1_flow_id}/segments?timerange={input_1_timerange!s}"
        ) as resp:
            resp.raise_for_status()
            flow_1_segments = await resp.json()

        for segment in flow_1_segments:
            async with post_request(
                session,
                credentials,
                f"{tams_url}/flows/{output_flow_id}/segments",
                json=mediajson.encode_value({
                    "object_id": segment["object_id"],
                    "timerange": segment["timerange"]
                })
            ) as resp:
                resp.raise_for_status()
                print(f"Added segment from Flow {input_1_flow_id} from and to timerange {segment['timerange']}")

        # Add segments from input 2 to output after the input 1 segments
        if flow_1_segments:
            seg_tr = TimeRange.from_str(segment["timerange"])
            if seg_tr.includes_end():
                part_2_offset = seg_tr.end + Timestamp.from_count(1, Fraction(50))
            else:
                part_2_offset = seg_tr.end
        else:
            part_2_offset = Timestamp(0)

        async with get_request(
            session,
            credentials,
            f"{tams_url}/flows/{input_2_flow_id}/segments?timerange={input_2_timerange!s}"
        ) as resp:
            resp.raise_for_status()
            flow_2_segments = await resp.json()

        seg_tr_offset = None
        for segment in flow_2_segments:
            seg_tr = TimeRange.from_str(segment["timerange"])

            # Calculate the offset to place the segment on the output flow timeline starting
            # at `part_2_offset`
            if seg_tr_offset is None:
                seg_tr_offset = part_2_offset - seg_tr.start

            new_seg_tr = TimeRange(
                seg_tr.start + seg_tr_offset,
                seg_tr.end + seg_tr_offset,
                seg_tr.inclusivity
            )

            # The media timeline started at zero when the ingest started, so `ts_offset` indicates what must be
            # added to the media time to get the Flow time.
            # So we can calculate media time at the start of the segment
            seg_offset = Timestamp.from_str(segment["ts_offset"])
            media_time = seg_tr.start - seg_offset

            # Now we want to know what to add to that media time to get the new start time
            new_ts_offset = new_seg_tr.start - media_time

            async with post_request(
                session,
                credentials,
                f"{tams_url}/flows/{output_flow_id}/segments",
                json=mediajson.encode_value({
                    "object_id": segment["object_id"],
                    "timerange": new_seg_tr,
                    "ts_offset": new_ts_offset
                })
            ) as resp:
                resp.raise_for_status()
                print(f"Added segment from Flow {input_2_flow_id} and timerange {segment['timerange']} to {new_seg_tr!s}")


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="simple_edit",
        description="Concatenate segments from 2 flows into a new flow"
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
        "--input1-flow-id", type=UUID, required=True,
        help="Input 1 Flow ID"
    )
    parser.add_argument(
        "--input1-timerange", type=TimeRange.from_str, default=TimeRange.eternity(),
        help="Input 1 timerange"
    )
    parser.add_argument(
        "--input2-flow-id", type=UUID, required=True,
        help="Input 2 Flow ID"
    )
    parser.add_argument(
        "--input2-timerange", type=TimeRange.from_str, default=TimeRange.eternity(),
        help="Input 2 timerange"
    )
    parser.add_argument(
        "--output-flow-id", type=UUID,
        help="Output Flow ID. Default is to generate an ID"
    )
    parser.add_argument(
        "--output-source-id", type=UUID,
        help="Output Source ID. Default is to generate an ID"
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

    output_timerange = asyncio.run(simple_edit(
        args.tams_url.rstrip("/"),
        credentials,
        args.input1_flow_id,
        args.input1_timerange,
        args.input2_flow_id,
        args.input2_timerange,
        args.output_flow_id or uuid4(),
        args.output_source_id or uuid4()
    ))
