# coding: utf-8
import logzero
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.options import options, define
from logzero import logger
from tasks.TaskTimer import TaskTimer
from web.entry import make_app
from web.models import create_db
from web.settings import sys_port, timer_loop
from web.utils.cache import jsapi_ticket
from web.utils.tools import machine_ip
from web.utils.z_logger import init_logger
from tasks.collector import SariDataCollector, run
from web.task import fetch_data

define("t", default=False, help="create table", type=bool)
define("init", default=False, help="init data", type=bool)
define("region", default=False, help="region data", type=bool)
define("cache", default=False, help="cache wechat data", type=bool)
define("filename", default=None, help="log file", type=str)
define("level", default='DEBUG', help="log level", type=str)
define("maxSize", default=5000, help="log size", type=int)
define("backupCount", default=5, help="backup time", type=int)


def log_func(handler):
    if handler.get_status() < 400:
        log_method = logzero.logger.info
    elif handler.get_status() < 500:
        log_method = logzero.logger.warning
    else:
        log_method = logzero.logger.error
    request_time = 1000.0 * handler.request.request_time()
    log_method("%d %s %s [%s] %.2fms",
               handler.get_status(), handler.request.method,
               handler.request.uri, handler.request.remote_ip,
               request_time)


def server():
    options.parse_command_line()
    init_logger(options.filename, options.level, options.maxSize, options.backupCount)
    if options.t:
        create_db.run()
    elif options.init:
        logger.info("准备疫情数据初始化")
        SariDataCollector(init=True).run()
        logger.info("疫情数据初始化完成")
    elif options.cache:
        logger.info("准备微信参数缓存")
        jsapi_ticket()
        logger.info("微信参数缓存完成")
    elif options.region:
        logger.info("准备地区数据")
        fetch_data()
        logger.info("准备地区数据")
    else:
        logger.info("启动疫情数据定时采集开始启动")
        timer = TaskTimer()
        timer.join_task(run, [], interval=timer_loop)
        timer.join_task(jsapi_ticket, [], interval=7100)
        timer.start()
        logger.info("启动疫情数据定时采集启动成功")
        app = make_app(None, log_func)
        http_Server = HTTPServer(app, max_buffer_size=504857600, max_body_size=504857600)
        http_Server.listen(sys_port)
        logger.info("==listen on port http://%s:%d ==", machine_ip(), sys_port)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    try:
        server()
    except KeyboardInterrupt as e:
        logger.info("==The server has been shut down==")
    except Exception as e:
        logger.exception(f"Exception Exit: {e}")
