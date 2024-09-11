import logging
import time

from log_organizer import LogOrganizer


logger = logging.getLogger('main')

try:
    lo = LogOrganizer()
    lo.set_stream_logger('main', )
    lo.set_stream_logger('test')
    # lo.set_file_logger('main') or lo.set_stream_logger('main', file_logger=True)
    for x in range(5):
        logger.info(f't_{x}')
        time.sleep(10)

    # main에 포함되지 않는 로거
    l2 = logging.getLogger('test')
    l2.error('error?')

    # 관리되지 않는 로거
    l3 = logging.getLogger('test2')
    l3.critical('critical?')

finally:
    lo.close()


# def main():
#     ...

# if __name__ == '__main__':
#     main()
