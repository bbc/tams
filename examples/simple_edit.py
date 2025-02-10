#!/usr/bin/env python
# This script demonstrates a simple edit of 2 Flows using segment metadata only

import asyncio
from collections import deque
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

FLOW_FRAME_RATE = 50

async def put_flow(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    tams_url: str,
    flow_id: UUID,
    source_id: UUID,
    custom_tags: dict[str, str] = {}
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
                "numerator": FLOW_FRAME_RATE,
                "denominator": 1
            },
            "frame_width": 1920,
            "frame_height": 1080,
            "bit_depth": 8,
            "interlace_mode": "progressive",
            "component_type": "YCbCr",
            "horiz_chroma_subs": 2,
            "vert_chroma_subs": 2
        },
        "tags": custom_tags
    }

    logger.info(f"Creating Flow {flow_id}")

    async with put_request(
        session,
        credentials,
        f"{tams_url}/flows/{flow_id}",
        json=flow_metadata
    ) as resp:
        resp.raise_for_status()


async def get_segments(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    tams_url: str,
    flow_id: UUID,
    timerange: TimeRange
) -> list[dict]:
    """Fetch a single page of segments from the given Flow"""
    async with get_request(
        session,
        credentials,
        f"{tams_url}/flows/{flow_id}/segments?timerange={timerange!s}"
    ) as resp:
        resp.raise_for_status()
        return await resp.json()


async def get_flow(
    session: aiohttp.ClientSession,
    credentials: Credentials,
    tams_url: str,
    flow_id: UUID
) -> dict:
    async with get_request(
        session,
        credentials,
        f"{tams_url}/flows/{flow_id}"
    ) as resp:
        resp.raise_for_status()
        return await resp.json()


async def simple_edit(
    tams_url: str,
    credentials: Credentials,
    input_1_flow_id: UUID,
    input_1_timerange: TimeRange,
    input_2_flow_id: UUID,
    input_2_timerange: TimeRange,
    output_flow_id: UUID,
    output_source_id: UUID,
) -> None:
    """Add timerange of segments from input 1 followed by a timerange of segments from input 2"""
    async with aiohttp.ClientSession() as session:
        await put_flow(session, credentials, tams_url, output_flow_id, output_source_id)

        # Add segments from input 1 to output
        flow_1_segments = await get_segments(session, credentials, tams_url, input_1_flow_id, input_1_timerange)

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
                part_2_offset = seg_tr.end + Timestamp.from_count(1, Fraction(FLOW_FRAME_RATE))
            else:
                part_2_offset = seg_tr.end
        else:
            part_2_offset = Timestamp(0)

        flow_2_segments = await get_segments(session, credentials, tams_url, input_2_flow_id, input_2_timerange)

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

        print(f"Finished writing output {output_flow_id}")


async def interval_edit(
    tams_url: str,
    credentials: Credentials,
    input_1_flow_id: UUID,
    input_1_timerange: TimeRange,
    input_2_flow_id: UUID,
    input_2_timerange: TimeRange,
    output_flow_id: UUID,
    output_source_id: UUID,
    cut_interval_sec: float
) -> None:
    """Cut between inputs 1 and 2 at fixed interval. Note: this will only handle a single page of segments"""
    cut_interval_ts = Timestamp.from_millisec(int(cut_interval_sec * 1000))

    edit_rate = Fraction(FLOW_FRAME_RATE, 1)

    custom_tags = {
        "_copy_edit_mode": "interval",
        "_copy_edit_interval": cut_interval_ts.to_sec_nsec()
    }

    async with aiohttp.ClientSession() as session:
        # Create output Flow
        await put_flow(session, credentials, tams_url, output_flow_id, output_source_id, custom_tags=custom_tags)

        flow_1_segments = deque(await get_segments(session, credentials, tams_url, input_1_flow_id, input_1_timerange))
        flow_2_segments = deque(await get_segments(session, credentials, tams_url, input_2_flow_id, input_2_timerange))
        working_time = Timestamp.from_str("0:0")

        next_switch_at = working_time + cut_interval_ts

        current_seg = {
            "id": input_1_flow_id,
            "list": flow_1_segments,
            "timeshift": TimeRange.from_str(flow_1_segments[0]["timerange"]).start
        }
        other_seg = {
            "id": input_2_flow_id,
            "list": flow_2_segments,
            "timeshift": TimeRange.from_str(flow_2_segments[0]["timerange"]).start
        }

        while (len(flow_1_segments) > 0 and len(flow_2_segments) > 0):
            position_in_flow_timeline = working_time + current_seg["timeshift"]

            # Draw a segment from the current list (and drop segments if we've passed them)
            next_seg = current_seg["list"][0]
            next_seg_tr = TimeRange.from_str(next_seg["timerange"]).normalise(edit_rate.numerator,
                                                                              edit_rate.denominator)
            if next_seg_tr.ends_earlier_than_timerange(position_in_flow_timeline):
                print(f"Segment {next_seg_tr} is before current position {position_in_flow_timeline} - dropping")
                current_seg["list"].popleft()
                continue

            next_seg_ts_offset = Timestamp.from_str(next_seg.get("ts_offset", "0:0"))

            # Work out how many seconds into the underlying segment we start
            seg_start_offset = (working_time + current_seg["timeshift"]) - next_seg_tr.start

            # Work out how much of the segment to include in the output
            segment_length_remaining = next_seg_tr.end - position_in_flow_timeline
            remaining_time_in_cut = next_switch_at - working_time

            # Note that for non-integer media rates this simple approach may lead to rounding anomalies
            # however this approach is used to keep the example simple.
            if (remaining_time_in_cut < segment_length_remaining):
                # Rest of this cut fits in the current segment, so we can write a new segment
                new_seg_tr = TimeRange(working_time, next_switch_at, TimeRange.INCLUDE_START)
            else:
                 # We need to add all of the rest of this segment, and then some more of the next one before cutting
                new_seg_tr = TimeRange.from_start_length(working_time, segment_length_remaining,
                                                         TimeRange.INCLUDE_START)

            new_segment = {
                "object_id": next_seg["object_id"],
                "timerange": new_seg_tr,
                "ts_offset": next_seg_ts_offset - current_seg["timeshift"],
                "sample_offset": seg_start_offset.to_count(edit_rate.numerator, edit_rate.denominator),
                "sample_count": new_seg_tr.length.to_count(edit_rate.numerator, edit_rate.denominator)
            }

            async with post_request(
                session,
                credentials,
                f"{tams_url}/flows/{output_flow_id}/segments",
                json=mediajson.encode_value(new_segment)
            ) as resp:
                resp.raise_for_status()
                print(f"Added segment from Flow {current_seg['id']} and timerange {next_seg_tr} to {new_seg_tr!s}")

            # Advance our time pointer
            working_time = new_seg_tr.end

            if (remaining_time_in_cut <= segment_length_remaining):
                # We've finished this cut, so swap to the other Flow
                past_seg = current_seg
                current_seg = other_seg
                other_seg = past_seg

                next_switch_at += cut_interval_ts
            else:
                # Drop the fully consumed segment
                current_seg["list"].popleft()

        print(f"At least one Flow segment list exhausted: stopping writing output {output_flow_id}")


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
    parser.add_argument(
        "--cut-interval-sec", type=float, default=None,
        help="By default this script pulls a timerange from each input sequentially. Set this to a number of seconds "
             "to linger on each before cutting between them instead"
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

    if args.cut_interval_sec is not None:
        output_timerange = asyncio.run(interval_edit(
            args.tams_url.rstrip("/"),
            credentials,
            args.input1_flow_id,
            args.input1_timerange,
            args.input2_flow_id,
            args.input2_timerange,
            args.output_flow_id or uuid4(),
            args.output_source_id or uuid4(),
            args.cut_interval_sec
        ))
    else:
        output_timerange = asyncio.run(simple_edit(
            args.tams_url.rstrip("/"),
            credentials,
            args.input1_flow_id,
            args.input1_timerange,
            args.input2_flow_id,
            args.input2_timerange,
            args.output_flow_id or uuid4(),
            args.output_source_id or uuid4(),
        ))
