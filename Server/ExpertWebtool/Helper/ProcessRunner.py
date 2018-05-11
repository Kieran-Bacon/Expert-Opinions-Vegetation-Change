import concurrent.futures
import os
import sys
import random
import logging
import atexit

from ExpertRep import ExpertModelAPI
from ExpertRep import ClimateModelOutput

from ExpertWebtool import CMOSTORAGE
from ExpertWebtool.DatabaseHandler import DatabaseHandler as db

from . import recordModelMetrics, CMOStore

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def fit_model_and_write_db(model_id, username, qid, CMOs, scores):
    try:
        recordModelMetrics(identifier=model_id)  # Clear DB entries of records for this model
        _LOGGER.info("Metrics cleared for modelid={}, username={}".format(model_id, username))
        ExpertModelAPI().fit_unsupervised(model_id=model_id, data=CMOStore.models())
        _LOGGER.info("Model fit unsupervised completed for modelid={}, username={}".format(model_id, username))
        metrics = ExpertModelAPI().partial_fit(model_id=model_id, data=CMOs, targets=scores)
        _LOGGER.info("Model fit supervised completed for modelid={}, username={}".format(model_id, username))
        recordModelMetrics(identifier=model_id, metrics=metrics)
        _LOGGER.info("Metrics written to DB for modelid={}, username={}".format(model_id, username))
        
    except Exception as e:
        print(str(e)) # TODO


class SingletonDecorator:  # TODO(BEN) upon merge, move this to somewhere better
    def __init__(self, cls):
        self.cls = cls
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = self.cls(*args, **kwargs)
        return self.instance


@SingletonDecorator
class ProcessRunner:  # TODO(BEN) upon merge, move this to somewhere better
    _PROCESS_LOG = logging.getLogger("ProcessRunner")
    __instance = None

    def __init__(self, timeout=1e-3, num_processes=None):
        print("Called")
        self.proccess_results = []
        self.num_processes = num_processes
        self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=num_processes)
        self.timeout = timeout

        def join_all_threads():
            self._PROCESS_LOG.info("There are {} processes that need to be joined".format(len(self.proccess_results)))
            for proc in self.proccess_results:
                proc.result()
            self._PROCESS_LOG.info("ALL processes joined")

        atexit.register(join_all_threads)

    def add_process(self, *args, **kwargs):

        fn = fit_model_and_write_db
        new_processes = []
        for proc in self.proccess_results:
            try:
                proc.result(timeout=self.timeout)
            except concurrent.futures._base.TimeoutError:
                new_processes.append(proc)
            except concurrent.futures.process.BrokenProcessPool:
                pass # Dealt with below

        self.proccess_results = new_processes

        try:
            process = self.process_pool.submit(fn, *args, **kwargs)
        except concurrent.futures.process.BrokenProcessPool:
            self.process_pool.shutdown()  # Joins the previous process pool and creates a new one
            self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=self.num_processes)
            self.proccess_results = []
            process = self.process_pool.submit(fn, *args, **kwargs)

        self.proccess_results.append(process)