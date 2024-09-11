import logging
import logging.handlers
import os
import traceback

from multiprocessing import Queue
from pathlib import Path
from threading import Thread


def get_parents_path(path: str, level: int = 0):
    path_object = Path(path)
    return path_object.parents[level]


STRING_EFFECT = '\033[2m'
COLORS = {
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'BRIGHT_GREEN': f'{STRING_EFFECT}\033[92m',
    'BRIGHT_YELLOW': f'{STRING_EFFECT}\033[93m',
    'BRIGHT_BLUE': f'{STRING_EFFECT}\033[94m',
    'BRIGHT_MAGENTA': f'{STRING_EFFECT}\033[95m',
    'BRIGHT_CYAN': f'{STRING_EFFECT}\033[96m',
    'RED': '\033[31m',
    'RESET_ALL': '\033[0m',
}


class LogOrganizer:
    '''
    한 파이썬 프로그램 내 발생하는 모든 로그에 대한 관리를 한 번에 진행하는 class입니다.
    posix 시스템에 대해서는 멀티프로세스 내 로그도 같이 모을 수 있으나, nt 시스템에서는
    멀티프로세스 내 로그가 공유되지 않습니다.
    하루에 한 번씩 이전 로그가 분리되어 저장됩니다.
    
    사용 시 다음과 같은 구조를 추천합니다.
    try:
        log_organizer = LogOrganizer(name='test')
        log_organizer.set_stream_logger('main', 0)
        log_organizer.set_stream_logger('main', 10)
        main()
    finally:
        log_organizer.close()
    '''

    def __init__(self, name: str = 'total', qsize: int = 500):
        '''
        로그 관련 프로세스를 시작합니다.
        멀티프로세스 queue를 이용합니다.
        '''
        
        self.repr_name = name
        self.listener = None
        self.log_queue = Queue(maxsize=qsize)
        self.occupied_color_index = 0

        # define log colors
        self.colors_list = list(COLORS.values())
        self.default_format = COLORS['RESET_ALL']

        # make log directory
        self._make_log_dir(name)
        self._init()

    def _make_log_dir(self, name: str):
        '''
        로그를 저장할 디렉토리를 지정합니다.
        /app 경로가 존재하면 Docker 내 시스템이라고 판단하여 app 경로 아래에, 그렇지 않으면 
        현재 log_organizer 경로보다 한 단계 위 디렉토리에 폴더를 생성합니다.       
        '''
        if os.path.exists('/app'):
            self.base_log_dir = os.path.join('/app', 'logs', name)
        else:
            self.base_log_dir = os.path.join(get_parents_path(__file__, 1), 'logs', name)
        os.makedirs(self.base_log_dir, exist_ok=True)

    def _start_listening(self, name: str):
        '''
        여러 프로세스에서 발생한 log를 모은 queue에서 소비하는 thread 를 시작합니다.
        '''
        self.listener = Thread(target=self._consume_log_queue, args=(name, ))
        self.listener.start()

    def _end_listening(self):
        '''
        queue에 종료 시그널을 보내고 스레드가 종료될 때까지 대기합니다.
        '''
        self.log_queue.put(None)
        self.listener.join()

    def _set_time_rotating_file_logger(self, name: str, backup_count: int = 100) -> logging.Logger:
        '''
        매 자정마다 각 로그를 분리하여 저장합니다.
        이 작업이 log_organizer를 통하지 않을 경우 여러 프로세스나 스레드가 같은 파일에 접근 시
        파일 쓰기 권한 문제가 발생하게 됩니다. 이 문제를 해결 하기 위해 log_organizer가 구성되었습니다.
        '''
        logger = logging.getLogger(name)
        log_format = f"%(name)-12s | [%(asctime)s] %(levelname)8s | %(message)s"
        formatter = logging.Formatter(log_format)

        filehandler = logging.handlers.TimedRotatingFileHandler(os.path.join(self.base_log_dir, f'{name}.log'),
                                                                when='midnight', backupCount=backup_count, encoding='utf-8-sig')
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
        return logger

    def _consume_log_queue(self, name: str):
        '''
        로그 queue에 있는 로그를 가져와 작업을 진행하는 함수입니다.
        '''
        logger = self._set_time_rotating_file_logger(name)
        while True:
            try:
                record = self.log_queue.get()
                if record is None:
                    break
                logger.handle(record)
            except Exception:
                logger.error('logger organizer listener problem')
                logger.info(traceback.format_exc())

    def _set_queue_logger(self, name: str) -> logging.Logger:
        '''
        발생한 로그를 queue handler로 받아서 self.log_queue 넣도록 합니다.
        '''
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        qh = logging.handlers.QueueHandler(self.log_queue)
        logger.addHandler(qh)
        return logger

    def set_file_logger(self, name: str) -> logging.Logger:
        '''
        로그를 파일로 저장합니다. 필요 시 각 로그 별로 따로 저장할 수 있습니다.
        기본적으로는 repr_name으로 지정된 대표 파일 하나로만 저장합니다.
        '''
        logger = logging.getLogger(name)
        log_format = f"{name:<12} | [%(asctime)s] %(levelname)8s | %(message)s"
        formatter = logging.Formatter(log_format)

        filehandler = logging.FileHandler(filename=os.path.join(self.base_log_dir, f'{name}.log'), encoding='utf-8-sig')
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
        return logger

    def set_stream_logger(self, name: str, color_index: int = -1, file_logger=False) -> logging.Logger:
        '''
        프로그램 내에서 name으로 된 logger 를 가져와서 하나의 파일로 저장하고, 특정한 색을 지정하여 보여줍니다.
        "main         | [2024-09-06 08:30:41,301]     INFO | log" 와 포맷이 지정되며,
        표시 시 지정된 색을, 저장 시에는 그대로 저장됩니다.

        green, yellow, blue, magenta, cyan 5개 순, 같은 순서로 밝은 톤으로 한 번 반복,
        마지막 10 index는 red 입니다.
        color_index를 지정하지 않아도 auto increment가 적용됩니다.
        '''
        logger = logging.getLogger(name)

        if color_index < 0:
            color_index = self.occupied_color_index
            self.occupied_color_index += 1

        color = self.colors_list[color_index % len(self.colors_list)]
        colored_log_format = f"{color}{name:<12} | [%(asctime)s] %(levelname)8s | %(message)s {self.default_format}"

        colered_formatter = logging.Formatter(colored_log_format)

        streamhandler = logging.StreamHandler()
        streamhandler.setLevel(logging.INFO)
        streamhandler.setFormatter(colered_formatter)
        logger.addHandler(streamhandler)

        self._set_queue_logger(name)
        if file_logger:
            self.set_file_logger(name)

        return logger

    def _init(self):
        self._start_listening(self.repr_name)

    def close(self):
        '''
        로깅 작업을 종료합니다.
        log_organizer는 multiprocess queue를 이용하므로, 프로세스를 kill 하지 않는 한 자동으로 종료되지 않습니다.
        keyboard interrupt도 무시하므로, try - finally 구문 등으로 묶어두는 것을 추천합니다.
        프로세스가 자동 종료되지 않는 것이 문제이며 close를 하지 않을 경우 그 이외 문제는 없습니다.
        '''
        self._end_listening()
