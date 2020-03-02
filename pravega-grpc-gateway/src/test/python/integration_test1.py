#!/usr/bin/env python

import logging
import grpc
import pravega
import base64
import gzip
import argparse
import uuid
import datetime


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('--gateway', default='localhost:54672')
    parser.add_argument('--scope', default='examples')
    args = parser.parse_args()
    logging.info('args=%s' % str(args))

    with grpc.insecure_channel(args.gateway) as pravega_channel:
        pravega_client = pravega.grpc.PravegaGatewayStub(pravega_channel)

        # Create scope
        request = pravega.pb.CreateScopeRequest(scope=args.scope)
        logging.info('CreateScope request=%s' % request)
        response = pravega_client.CreateScope(request)
        logging.info('CreateScope response=%s' % response)

        # Create stream
        stream = 'test-%s' % str(uuid.uuid4())
        request = pravega.pb.CreateStreamRequest(
            scope=args.scope,
            stream=stream,
            scaling_policy=pravega.pb.ScalingPolicy(min_num_segments=1),
        )
        logging.info('CreateStream request=%s' % request)
        response = pravega_client.CreateStream(request)
        logging.info('CreateStream response=%s' % response)

        # Write events
        events_to_write = [
            pravega.pb.WriteEventsRequest(
                scope=args.scope,
                stream=stream,
                event=str(datetime.datetime.now()).encode(encoding='UTF-8'),
                routing_key='0',
            ),
            pravega.pb.WriteEventsRequest(
                scope=args.scope,
                stream=stream,
                event=str(datetime.datetime.now()).encode(encoding='UTF-8'),
                routing_key='0',
            ),
        ]
        logging.info("events_to_write=%s", events_to_write)
        write_response = pravega_client.WriteEvents(iter(events_to_write))
        logging.info("WriteEvents response=" + str(write_response))

        # Get stream info
        stream_info = pravega_client.GetStreamInfo(pravega.pb.GetStreamInfoRequest(scope=args.scope, stream=stream))
        logging.info('GetStreamInfo response=%s' % stream_info)

        # Read events
        read_events_request = pravega.pb.ReadEventsRequest(
            scope=args.scope,
            stream=stream,
            from_stream_cut=stream_info.head_stream_cut,
            to_stream_cut=stream_info.tail_stream_cut,
        )
        logging.info('ReadEvents request=%s', read_events_request)
        read_events_response = list(pravega_client.ReadEvents(read_events_request))
        logging.info('ReadEvents response=%s', read_events_response)

        # Fetch single event from event pointer
        for _ in range(10):
            event_pointer = read_events_response[0].event_pointer
            fetch_event_request = pravega.pb.FetchEventRequest(
                scope=args.scope,
                stream=stream,
                event_pointer=event_pointer,
            )
            logging.info('FetchEvent request=%s', fetch_event_request)
            fetch_event_response = pravega_client.FetchEvent(fetch_event_request)
            logging.info('FetchEvent response=%s', fetch_event_response)

        # Delete stream
        request = pravega.pb.DeleteStreamRequest(
            scope=args.scope,
            stream=stream,
        )
        logging.info('DeleteStream request=%s' % request)
        response = pravega_client.DeleteStream(request)
        logging.info('DeleteStream response=%s' % response)


if __name__ == '__main__':
    main()