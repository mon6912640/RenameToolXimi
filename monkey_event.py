# encoding: UTF-8
# 系统模块
from queue import Queue, Empty
from threading import *

from typing import *

########################################################################
"""事件对象"""


class EventVo:
    # 事件类型
    type = ''
    # 事件附带数据
    data = None

    def __init__(self, p_type=None, p_data=None):
        self.type = p_type  # 事件类型
        self.data = p_data


########################################################################
class EventDispatcherAsync:
    """
    基于线程的异步事件发送器
    """
    __thread: Thread = None
    __use_thread = True

    # ----------------------------------------------------------------------
    def __init__(self):
        """初始化事件管理器"""
        # 事件对象列表
        self.__eventQueue = Queue()
        # 事件管理器开关
        self.__active = False
        # 事件回调个数
        self.__handler_count = 0

        # 这里的__handlers是一个字典，用来保存对应的事件的响应函数
        # 其中每个键对应的值是一个列表，列表中保存了对该事件监听的响应函数，一对多
        self.__handlers_map = {}

    def setup(self, p_use_thread=True):
        self.__use_thread = p_use_thread
        if p_use_thread:
            # 事件处理线程
            self.__thread = Thread(target=self.__run)
        else:
            pass

    # ----------------------------------------------------------------------
    def __run(self):
        """引擎运行"""
        while self.__active is True:
            try:
                # 获取事件的阻塞时间设为1秒
                event = self.__eventQueue.get(block=True, timeout=1)
                self.__event_process(event)
            except Empty:
                pass

    # ----------------------------------------------------------------------
    def __event_process(self, p_event: EventVo):
        """处理事件"""
        # 检查是否存在对该事件进行监听的处理函数
        if p_event.type in self.__handlers_map:
            # 若存在，则按顺序将事件传递给处理函数执行
            for handler in self.__handlers_map[p_event.type]:
                handler(p_event)

    # ----------------------------------------------------------------------
    def start(self):
        """启动"""
        # 将事件管理器设为启动
        if self.__active:
            return
        self.__active = True
        if self.__thread:
            # 启动事件处理线程
            self.__thread.start()

    # ----------------------------------------------------------------------
    def stop(self):
        """停止"""
        # 将事件管理器设为停止
        if not self.__active:
            return
        self.__active = False
        if self.__thread:
            # 等待事件处理线程退出
            self.__thread.join()

    # ----------------------------------------------------------------------
    def add_event(self, p_type: str, p_handler):
        """
        添加事件侦听
        :param p_type:
        :param p_handler:
        :return:
        """
        # 尝试获取该事件类型对应的处理函数列表，若无则创建
        try:
            handler_list = self.__handlers_map[p_type]
        except KeyError:
            handler_list = []

        self.__handlers_map[p_type] = handler_list
        # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
        if p_handler not in handler_list:
            handler_list.append(p_handler)
            self.__handler_count += 1
            self.start()

    # ----------------------------------------------------------------------
    def remove_event(self, p_type: str, p_handler):
        if p_type not in self.__handlers_map:
            return
        handler_list: List = self.__handlers_map[p_type]
        if p_handler in handler_list:
            handler_list.remove(p_handler)
            self.__handler_count -= 1

    # ----------------------------------------------------------------------
    def send_event(self, p_type: str, p_data=None):
        """发送事件，向事件队列中存入事件"""
        self.__eventQueue.put(EventVo(p_type, p_data))


########################################################################
"""全局对象"""
"""异步事件中心"""
EventCenterAsync: EventDispatcherAsync = EventDispatcherAsync()


########################################################################
class CallBackVo:
    uid = 0
    type = ''
    data = None
    callback = None
    priority = 0


class TypeVo:
    type = ''
    calling_value = 0
    callback_list: List[CallBackVo] = None

    def __init__(self):
        # 这里有个坑，引用类型的实例变量，不能在定义时候初始化，一定需要在初始化函数里面初始化
        # 否则多个实例引用的都是同一个内存的引用类型
        self.callback_list = []


class EventDispatcherSync:
    """
    同步的事件发送器
    """

    def __init__(self):
        self.__type_vo_map: Dict[str, TypeVo] = {}
        self.__callback_vo_map: Dict[int, CallBackVo] = {}
        pass

    # ----------------------------------------------------------------------
    def get_callback_vo_by_uid(self, p_uid) -> CallBackVo:
        if p_uid in self.__callback_vo_map:
            return self.__callback_vo_map[p_uid]

    # ----------------------------------------------------------------------
    def get_type_vo_by_type(self, p_type):
        if p_type in self.__type_vo_map:
            return self.__type_vo_map[p_type]

    # ----------------------------------------------------------------------
    def add_event(self, p_type: str, p_handler, p_priority: int = 0):
        """
        添加侦听
        :param p_type: 事件类型
        :param p_handler: 回调函数
        :param p_priority: 优先级 99比1的回调优先级高
        :return:
        """
        t_uid = id(p_handler)
        t_vo = self.get_callback_vo_by_uid(t_uid)
        if t_vo:
            return
        t_vo = CallBackVo()
        t_vo.type = p_type
        t_vo.uid = t_uid
        t_vo.callback = p_handler
        t_vo.priority = p_priority

        t_type_vo = self.get_type_vo_by_type(p_type)
        if not t_type_vo:
            t_type_vo = TypeVo()
            t_type_vo.type = p_type
            self.__type_vo_map[p_type] = t_type_vo
        elif t_type_vo.calling_value != 0:
            t_type_vo.callback_list = list(t_type_vo.callback_list)  # 复制回调列表

        t_list = t_type_vo.callback_list
        t_insert_index = -1
        for i in range(len(t_list)):
            if t_list[i].priority < t_vo.priority:
                t_insert_index = i
                break
        if t_insert_index > -1:
            t_list.insert(t_insert_index, t_vo)
        else:
            t_list.append(t_vo)
        self.__callback_vo_map[t_uid] = t_vo

    # ----------------------------------------------------------------------
    def remove_event(self, p_type: str, p_handler):
        """
        删除侦听
        :param p_type: 事件类型
        :param p_handler: 回调函数
        :return:
        """
        t_type_vo = self.get_type_vo_by_type(p_type)
        if not t_type_vo:
            return
        t_uid = id(p_handler)
        t_vo = self.get_callback_vo_by_uid(t_uid)
        if not t_vo:
            return
        t_list = t_type_vo.callback_list
        if len(t_list) < 1:
            return

        if t_type_vo.calling_value != 0:
            t_type_vo.callback_list = t_list = list(t_list)

        for i in range(len(t_list) - 1, -1, -1):
            t_vo = t_list[i]
            if t_vo.uid == t_uid:
                del t_list[i]
                del self.__callback_vo_map[t_uid]
                break

    # ----------------------------------------------------------------------
    def send_event(self, p_type, p_data=None):
        t_type_vo = self.get_type_vo_by_type(p_type)
        if not t_type_vo or not t_type_vo.callback_list:
            return
        t_list = t_type_vo.callback_list
        if len(t_list) < 1:
            return

        # 做个标记，防止外部修改原始数组导致遍历错误。这里不直接调用list.concat()因为dispatch()方法调用通常比on()等方法频繁。
        t_type_vo.calling_value += 1
        t_event = EventVo(p_type, p_data)
        for vo in t_list:
            vo.callback(t_event)  # 执行回调
        t_type_vo.calling_value -= 1


########################################################################
"""全局对象"""
"""同步事件中心"""
EventCenterSync: EventDispatcherSync = EventDispatcherSync()
