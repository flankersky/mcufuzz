import logging

class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, file_name, level='info',
                 fmt='[Target] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(file_name)
        self.file_name = file_name

        # 设置日志格式
        self.format_str = logging.Formatter(fmt)

        # 设置日志级别
        self.logger.setLevel(self.level_relations.get(level))

    def output_console(self):
        # 往屏幕上输出
        sh = logging.StreamHandler()
        sh.setFormatter(self.format_str)
        self.logger.addHandler(sh)
        return sh

    def output_file(self):
        # 将日志写到文件里面
        th = logging.FileHandler(self.file_name,
                                 encoding='utf-8')
        th.setFormatter(self.format_str)
        self.logger.addHandler(th)
        return th

    def remove_handler(self, handler):
        self.logger.removeHandler(handler)

    def __call__(self, message):
        sh = self.output_console()
        th = self.output_file()

        self.logger.info(message)

        self.remove_handler(sh)
        self.remove_handler(th)
if __name__ == '__main__':
    log = Logger('target.log', level='debug')
    for i in range(10):
        log(f'EPOCH {i}: loss:{i*0.1}, acc:{i}')
