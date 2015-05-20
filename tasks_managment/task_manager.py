__author__ = 'mandriy'

from threading import Lock


class TaskIdError(Exception):
    """ Exception is thrown in any case of task id error.
    """

    def __init__(self, message, task_id):
        Exception.__init__(self)
        self.task_id = task_id
        self.message = 'Handle error with id %s. Reason: %s.' % (task_id, message)

    def get_task_id(self):
        """
        :return: task id
        """
        return self.task_id


class EmptyTaskStack(Exception):
    """ Exception is thrown in case of trying to take new task from empty system.
    """

    def __init__(self, msg):
        Exception.__init__(self, msg)


class Task:
    """ Single task representation
    """

    def __init__(self, task_rep):
        if isinstance(task_rep, Task):
            self.__task_rep__ = task_rep.get_task_rep()
        else:
            self.__task_rep__ = task_rep

    def get_task_rep(self):
        """
        :return: task representation
        """
        return self.__task_rep__


class ActiveTask(Task):
    """ Represents task which is already in process
    """

    def __init__(self, task_rep):
        Task.__init__(self, task_rep)
        self.__active_nodes__ = 0
        self.__done__ = False

    def is_done_task(self):
        """
        :return: boolean value which tells whether task is done
        """
        return self.__done__

    def mark_as_done(self):
        """
        Marks task as done.
        :return: None
        """
        self.__done__ = True

    def no_active_nodes(self):
        """
        :return: boolean value which tells whether task don't have active nodes.
        """
        return self.__active_nodes__ == 0

    def active_nodes(self):
        """
        :return: number of active nodes
        """
        return self.__active_nodes__

    def lock_node(self):
        """
        :return: increment active nodes counter
        """
        self.__active_nodes__ += 1

    def release_node(self):
        """
        :return: decrement active nodes counter in case of counter is already zero raises an Exception
        """
        if self.__active_nodes__ != 0:
            self.__active_nodes__ -= 1
        else:
            raise Exception('There is no locked nodes.')


class AvailableTask(Task):
    """ Represents task which is waiting to be processed
    """
    pass


class DoneTask(Task):
    """ Represents task which is already done.
    """

    def __init__(self, task_rep, result):
        Task.__init__(self, task_rep)
        self.__result__ = result

    def get_result(self):
        """
        :return: saved result done of task
        """
        return self.__result__


class TaskStack:
    """ Represents thread safe system task with basic interface
    """

    def __init__(self):
        self.__max_task_id__ = 1
        self.__available_tasks__ = {}
        self.__active_tasks__ = {}
        self.__done_tasks__ = {}
        self.__mutex__ = Lock()

    def __submit_task__(self, task_id, result):
        """
        submit task inner representation func which have to be overridden by subclasses.
        """
        raise Exception('Abstract method call.')

    def __rollback_task__(self, task_id):
        """
        rollback task inner representation func which have to be overridden by subclasses.
        """
        raise Exception('Abstract method call.')

    def __get_task__(self):
        """
        get task inner representation func which have to be overridden by subclasses.
        """
        raise Exception('Abstract method call.')

    def __accept_task__(self, task_id):
        """
        accept task inner representation func which have to be overridden by subclasses.
        """
        raise Exception('Abstract method call.')

    def __cover__(self, cover_func, *args):
        """
        Covers func in order to do it thread safe.
        :param cover_func: func which will be covered
        :param args: arguments for func
        :return: result of covered func
        """
        try:
            self.__mutex__.acquire()
            return cover_func(*args)
        finally:
            self.__mutex__.release()

    def system_snapshot(self):
        """
        :return: system state
        """
        return self.__cover__(lambda: {"active": len(self.__active_tasks__),
                                       "available": len(self.__available_tasks__),
                                       "done": len(self.__done_tasks__)})

    def submit_task(self, task_id, result):
        """
        Save task result.
        :param task_id: identify task which is submitted
        :param result: result of task processing
        """
        return self.__cover__(self.__submit_task__, task_id, result)

    def accept_task(self, task_id):
        """
        Tells system that task is in process.
        :param task_id: identify task which is in process
        """
        self.__cover__(self.__accept_task__, task_id)

    def rollback_task(self, task_id):
        """
        Tells system to rollback one node.
        :param task_id:
        :return:
        """
        return self.__cover__(self.__rollback_task__, task_id)

    def get_task(self):
        """
        :return: task
        """
        return self.__cover__(self.__get_task__)

    def work_is_done(self):
        """
        :return: boolean value which tells whether all tasks are done
        """
        return self.__cover__(lambda: len(self.__active_tasks__) == 0 and len(self.__available_tasks__) == 0)

    def done_part(self):
        """
        :return: results of currently done tasks
        """
        return self.__cover__(lambda: map(lambda done_task: done_task.get_result(),
                                          self.__done_tasks__.values()))


class TextTaskStack(TaskStack):
    """ Represents text task system where task is simple text array.
    """

    def __init__(self):
        TaskStack.__init__(self)

    def load_tasks(self, texts):
        """
        Adds texts into available tasks stack.
        :param texts: texts are tasks
        :return: None
        """
        self.__mutex__.acquire()
        for text in texts:
            self.__available_tasks__[self.__max_task_id__] = AvailableTask(text)
            self.__max_task_id__ += 1
        self.__mutex__.release()

    def __get_task__(self):
        if self.__available_tasks__.keys():
            task_id = self.__available_tasks__.keys()[0]
            self.__active_tasks__[task_id] = ActiveTask(self.__available_tasks__[task_id])
            del self.__available_tasks__[task_id]
            return task_id, self.__active_tasks__[task_id].get_task_rep()
        else:
            if self.__active_tasks__.keys():
                active_tasks = self.__active_tasks__.items()[:]
                active_tasks.sort(key=lambda task: task[1].active_nodes())
                task_id = active_tasks[0][0]
                return task_id, self.__active_tasks__[task_id].get_task_rep()
            else:
                raise EmptyTaskStack("There is no available tasks.")

    def __submit_task__(self, task_id, result):
        if task_id in self.__active_tasks__:
            if not self.__active_tasks__[task_id].is_done_task():
                self.__active_tasks__[task_id].mark_as_done()
                self.__done_tasks__[task_id] = DoneTask(self.__active_tasks__[task_id],
                                                        result)
            self.__rollback_task__(task_id)
        else:
            raise TaskIdError("Trying to submit result of task which is inactive.", task_id)

    def __rollback_task__(self, task_id):
        if task_id in self.__active_tasks__:
            rollback_task = self.__active_tasks__[task_id]
            rollback_task.release_node()
            if rollback_task.no_active_nodes():
                if not rollback_task.is_done_task():
                    self.__available_tasks__[task_id] = AvailableTask(self.__active_tasks__[task_id])
                del self.__active_tasks__[task_id]
        else:
            raise TaskIdError("Trying to rollback inactive task.", task_id)

    def __accept_task__(self, task_id):
        if task_id in self.__active_tasks__:
            self.__active_tasks__[task_id].lock_node()
        else:
            raise TaskIdError("Trying to accept inactive task.", task_id)


