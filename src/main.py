from platforms.default import Default
from platforms.platform import Platform
from platforms.youtube import Youtube
from utils import cleanup, load_file_link, parse_url
from worker_manager import WorkerManger
import argparse
import signal
import sys


def get_platfrom(link, **kwargs) -> Platform:
    url_obj = parse_url(link)
    if "youtube" in url_obj["hostname"]:
        return Youtube(**kwargs)
    return Default(**kwargs)


def download(args):

    cleanup(args.savepath)
    kwargs = {"savepath": args.savepath, "retry": args.retry}

    work = []
    if args.filename:
        for link in load_file_link(args.filename):
            work = work + get_platfrom(link, **kwargs).build_vedio(link)
    if args.playlist:
        work = work + get_platfrom(args.playlist, **kwargs).build_playlist(
            args.playlist
        )
    if args.link:
        work = work + get_platfrom(args.link, **kwargs).build_vedio(args.link)

    wm = WorkerManger(workers_count=args.workers, retry=args.retry, work=work)

    def signal_handler(sig, frame):
        cleanup(args.savepath)
        wm.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    wm.start()
    wm.join()
    wm.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="download content")
    parser.add_argument("-f", "--filename", type=str)
    parser.add_argument("-p", "--playlist", type=str)
    parser.add_argument("-a", "--link", type=str)
    parser.add_argument("-r", "--retry", type=int, default=10)
    parser.add_argument("-w", "--workers", type=int, default=3)
    parser.add_argument("-s", "--savepath", default="./", type=str)
    args = parser.parse_args()

    if not (args.filename or args.playlist or args.link):
        parser.error("Action requested, add --filename or --playlist")

    download(args)
