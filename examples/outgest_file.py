#!/usr/bin/env python
# This script demonstrates outgest of a TAMS Flow to a local file

from typing import AsyncGenerator
from argparse import ArgumentParser
from uuid import UUID
from io import BytesIO
import os
from fractions import Fraction
import asyncio
import logging

from mediatimestamp import Timestamp, TimeRange
import aiohttp
import av

from credentials import Credentials, BasicCredentials, OAuth2ClientCredentials
from client import get_request

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def get_flow(tams_url: str, credentials: Credentials, flow_id: UUID) -> dict:
    """Returns a Flow dict for the given Flow ID"""
    flow_url = f"{tams_url}/flows/{flow_id}"
    async with aiohttp.ClientSession() as session:
        async with get_request(session, credentials, flow_url) as resp:
            resp.raise_for_status()
            return await resp.json()


async def get_flow_segments(
    tams_url: str,
    credentials: Credentials,
    flow: dict,
    timerange: TimeRange
) -> AsyncGenerator[dict, None]:
    """Generator of Flow Segment dicts for the given Flow ID and timerange"""
    segments_url = f"{tams_url}/flows/{flow['id']}/segments?timerange={timerange!s}"
    async with aiohttp.ClientSession() as session:
        while True:
            async with get_request(session, credentials, segments_url) as resp:
                resp.raise_for_status()

                segments = await resp.json()
                for segment in segments:
                    segment_timerange = TimeRange.from_str(segment["timerange"])
                    if segment_timerange.overlaps_with_timerange(timerange):
                        yield segment
                    else:
                        logger.warning(
                            f"Skipping segment returned by TAMS with a timerange {segment_timerange!s} "
                            f"that does not overlap with the target timerange {timerange!s}"
                        )

                try:
                    segments_url = resp.links["next"]["url"]
                except KeyError:
                    break


def normalise_and_transfer_media(
    flow: dict,
    segment: dict,
    media_essence: BytesIO,
    av_output: av.container.OutputContainer,
    check_timing: bool
) -> TimeRange:
    """Transfer the essence from the media object to the output file.

    Also normalise the included sample range and timing using the Flow Segment information.
    """
    # Identify the stream in the input MPEG-TS container
    if "container_mapping" in flow:
        container_mapping = flow["container_mapping"]
        track_index = container_mapping.get("track_index")
        format_index = container_mapping.get("format_index")
    else:
        track_index = None
        format_index = 0

    if format_index is None and track_index is not None:
        demux_kwargs = {"streams": track_index}
    else:
        if format_index is None:
            format_index = 0

        if flow["format"] == "urn:x-nmos:format:video":
            demux_kwargs = {"video": format_index}
        elif flow["format"] == "urn:x-nmos:format:audio":
            demux_kwargs = {"audio": format_index}
        else:
            raise NotImplementedError()

    if flow["format"] == "urn:x-nmos:format:video":
        media_rate = Fraction(
            flow["essence_parameters"]["frame_rate"]["numerator"],
            flow["essence_parameters"]["frame_rate"].get("denominator", 1)
        )
    elif flow["format"] == "urn:x-nmos:format:audio":
        media_rate = Fraction(flow["essence_parameters"]["sample_rate"])
    else:
        raise NotImplementedError()

    try:
        discard_before_count = int(segment["sample_offset"])
    except KeyError:
        discard_before_count = 0

    try:
        keep_after_count = int(segment["sample_count"])
        if keep_after_count == 0:
            # Corner case - no media units are used from the segment
            return TimeRange.never()
    except KeyError:
        keep_after_count = -1

    ts_offset = Timestamp.from_str(segment.get("ts_offset", "0:0"))

    discarding_samples = discard_before_count > 0 or keep_after_count >= 0
    output_timerange = TimeRange.never()
    first_packet = True
    with av.open(media_essence, mode="r", format="mpegts") as av_input:
        for pkt in av_input.demux(**demux_kwargs):
            if pkt.dts is None and pkt.pts is None:
                continue

            # Undo the adjustment that ffmpeg MPEG-TS decoder makes if the input pts / dts
            # are close to the rollover point. ffmpeg positions the timing < 0 such that the rollover
            # happens around 0 rather than 2**33. This adjustment only applies to MPEG-TS which has
            # positive 33-bit resolution timestamps.
            if first_packet:
                if flow["container"] == "video/mp2t" and (
                        (pkt.pts is not None and pkt.pts < 0) or (pkt.dts is not None and pkt.dts < 0)):
                    ts_offset += Timestamp.from_count(2**33, Fraction(90000))
                    logging.info(
                        "Added 2**33@90kHz to ts_offset to undo the ffmpeg decode timing adjustment near rollover")

                first_packet = False

            if check_timing and pkt.pts is None:
                logger.warning(f"Packet has no pts set ({pkt.dts=}, {pkt.pts=}, {pkt.time_base=}, {pkt.size=})")

            # Don't attempt to get the media unit count if it isn't required to
            # process FlowSegment.sample_offset and sample_count. This avoids potential
            # NotImplementedError because the packet duration is not set.
            process_media_unit_count = discard_before_count > 0 or keep_after_count >= 0

            # Get the number of media units (samples) in the packet
            if process_media_unit_count:
                if pkt.duration is not None:
                    # We assume the packet duration is accurate enough to provide a media unit count
                    pkt_duration = Timestamp.from_count(pkt.duration, 1/pkt.time_base)
                else:
                    if flow["format"] == "urn:x-nmos:format:video":
                        # Assume the packet contains 1 video frame
                        pkt_duration = Timestamp.from_count(1, media_rate)
                    else:
                        raise NotImplementedError("Packet doesn't provide a duration")

                media_unit_count = pkt_duration.to_count(media_rate)

            # Discard media units before FlowSegment.sample_offset
            if process_media_unit_count and discard_before_count > 0:
                discard_before_count -= media_unit_count
                if discard_before_count < 0:
                    logger.warning(
                        "Segment 'sample_offset' is not a whole number of packets. "
                        f"Included {-discard_before_count} samples at the start. "
                        "A transcode would be required to get the correct number of samples"
                    )
                continue

            # Re-assign the packet to the output stream
            if len(av_output.streams) == 0:
                av_output.add_stream_from_template(pkt.stream)
            pkt.stream = av_output.streams[0]

            # Adjust the packet timing to place it on the Flow's timeline using FlowSegment.ts_offset
            if pkt.pts is not None:
                pkt.pts = pkt.pts + ts_offset.to_count(1/pkt.time_base)

                # Calculate the output (presentation) timerange. If no media units are discarded it
                # should end up equaling the FlowSegment.timerange
                pkt_pts_ts = Timestamp.from_count(pkt.pts, 1/pkt.time_base)
                incl_output_timerange = output_timerange.extend_to_encompass_timerange(
                    TimeRange.from_single_timestamp(pkt_pts_ts)
                )
                if pkt.duration is not None:
                    output_timerange = output_timerange.extend_to_encompass_timerange(
                        TimeRange.from_start_length(
                            pkt_pts_ts,
                            Timestamp.from_count(pkt.duration, 1/pkt.time_base),
                            TimeRange.INCLUDE_START
                        )
                    )
                else:
                    output_timerange = incl_output_timerange

            if pkt.dts is not None:
                pkt.dts = pkt.dts + ts_offset.to_count(1/pkt.time_base)

            av_output.mux([pkt])

            # Discard media units >= FlowSegment.sample_offset + FlowSegment.sample_count
            if process_media_unit_count and keep_after_count >= 0:
                keep_after_count -= media_unit_count
                if keep_after_count <= 0:
                    if keep_after_count < 0:
                        logger.warning(
                            "Segment 'sample_count' is not a whole number of packets. "
                            f"Included {-keep_after_count} samples at the end. "
                            "A transcode would be required to get the correct number of samples"
                        )
                    break

    if check_timing and not discarding_samples:
        # Warn if the normalised timerange calculated from the media pts and FlowSegment.ts_offset
        # does not equal the normalised FlowSegment.timerange.
        # Note that normalisation will hide differences that are less than 1/2 the media unit duration
        # and the assumption is that those differences are rounding errors
        segment_timerange = TimeRange.from_str(segment["timerange"]).normalise(media_rate)
        norm_output_timerange = output_timerange.normalise(media_rate)
        norm_segment_timerange = segment_timerange.normalise(media_rate)
        if norm_output_timerange != norm_segment_timerange:
            logger.warning(
                "Timerange calculated from media file timestamps and flow segment ts_offset, "
                f"{output_timerange!s}, does not equal the segment timerange, {segment_timerange!s}"
            )

    return output_timerange


async def outgest_file(
    tams_url: str,
    credentials: Credentials,
    flow_id: UUID,
    timerange: TimeRange,
    output_filename: str,
    check_timing: bool
) -> TimeRange:
    flow = await get_flow(tams_url, credentials, flow_id)

    # Support is limited to Flows with MPEG-TS media objects containing audio or video
    if "container" not in flow:
        raise NotImplementedError("Flow without a container is not supported")
    if flow["container"] != "video/mp2t":
        raise NotImplementedError(f"Flow container '{flow['container']}' is not supported")
    if flow["format"] not in ["urn:x-nmos:format:video", "urn:x-nmos:format:audio"]:
        raise NotImplementedError(f"Flow format '{flow['format']}' is not supported")

    output_timerange = TimeRange.never()
    with av.open(output_filename, mode="w", format="mpegts") as av_output:
        async with aiohttp.ClientSession() as media_object_session:
            async for segment in get_flow_segments(tams_url, credentials, flow, timerange):
                # Assuming the media object is small enough to load into memory. An alternative
                # would be to use streaming responses, although that's complicated here as
                # PyAV doesn't support async file / stream inputs.
                # An optimisation would be to add some concurrency by fetching media objects
                # in multiple asyncio tasks and to also use a queue + threads to parse and process
                # the packets.
                async with media_object_session.get(segment["get_urls"][0]["url"]) as resp:
                    resp.raise_for_status()
                    media_essence = BytesIO(await resp.read())

                # Note: not passing timerange to discard media units outside the target timerange.
                # This is because they may be needed for video precharge / audio priming or
                # video rollout / audio remainder. The output may therefore have more media than
                # that requested using the timerange.
                # An alternative is to take the timerange into account and then deal with precharge etc.
                # Formats such as MP4 could identify how much precharge etc. there is.

                seg_output_timerange = await asyncio.get_running_loop().run_in_executor(
                    None,
                    normalise_and_transfer_media,
                    flow,
                    segment,
                    media_essence,
                    av_output,
                    check_timing
                )
                output_timerange = output_timerange.extend_to_encompass_timerange(seg_output_timerange)

                logger.info(f"Outgested flow segment at {segment['timerange']}")

    return output_timerange


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="outgest_file",
        description="TAMS Flow outgest to file example"
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
        "--flow-id", type=UUID, required=True,
        help="Output media from this Flow"
    )
    parser.add_argument(
        "--output", type=str, required=True,
        help="The output filename"
    )
    parser.add_argument(
        "--timerange", type=TimeRange.from_str, default=TimeRange.eternity(),
        help="Timerange of media to output from the Flow"
    )
    parser.add_argument(
        "--check-timing", action="store_true",
        help="Enable timing checks"
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

    logger.info(f"Outputing timerange {args.timerange!s} of flow {args.flow_id} to {args.output}")
    if args.timerange.start is not None:
        logger.info(f"Timerange start as UTC is {args.timerange.start.to_iso8601_utc()}")
    if args.timerange.end is not None:
        logger.info(f"Timerange end as UTC is {args.timerange.end.to_iso8601_utc()}")

    output_timerange = asyncio.run(outgest_file(
        args.tams_url.rstrip("/"),
        credentials,
        args.flow_id,
        args.timerange,
        args.output,
        args.check_timing
    ))

    logger.info(f"Output timerange {output_timerange!s}")
