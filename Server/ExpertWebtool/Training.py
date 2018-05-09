from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc
import concurrent.futures
import sys
import random
import logging
import atexit

from ExpertRep import ExpertModelAPI, ClimateModelOutput

from . import CMOSTORAGE
from . import Helper
from .Helper import *
from .DatabaseHandler import DatabaseHandler as db

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@view_config(route_name="training", renderer="templates/training_main.html")
def training(request):
    permissions(request, authority=1)

    # Collect all question ids
    allQuestions = db.execute("collectQuestions", [])

    # Select questions the user still has unannotated models for
    questions = []
    for qInfo in allQuestions:
        if len(db.execute('collectUnlabelled', [request.session["username"], qInfo["qid"]])):
            questions.append({"qid": qInfo["qid"], "text": qInfo["text"]})

    return Helper.pageVariables(request, {"title": "Training Page", "questions": questions})


@view_config(route_name="collectModelKML", renderer="string")
def collectModelKML(request):
    cmo = ClimateModelOutput.load(os.path.join(CMOSTORAGE + request.matchdict['cmoid']))
    return cmo.get_kml(int(request.matchdict["layer"]))


@view_config(route_name="collectCMO", renderer="json")
def collectCMO(request):
    permissions(request)

    # Collect the question id from the request
    try:
        qid = int(request.params["qid"])
    except KeyError as e:
        raise exc.HTTPBadRequest("Question ID not passed")

    # Collect the collection of unlabelled models for that user and question
    unlabelled = db.execute('collectUnlabelled', [request.session["username"], qid])

    # Select and return a modelID at random
    # TODO: Include directed learning
    if len(unlabelled):
        modelID, = random.choice(unlabelled)
        return {"mid": modelID}

    # No models left to annotate, no model id to return
    raise exc.HTTPNoContent()


@view_config(route_name="scoreCMO")
def scoreCMO(request):
    permissions(request)

    # Collect information
    try:
        mid = int(request.params["mid"])
        qid = int(request.params["qid"])
        score = int(request.params["score"])
    except KeyError as e:
        raise exc.HTTPBadRequest("Necessary content is missing")

    # TODO: decide upon score range and values
    score = float(int(score)) * 0.05  # Reduce score to between 0-5

    # Record the users opinion
    db.execute('labelModel', [request.session["username"], qid, mid, score])

    raise exc.HTTPNoContent()


def fit_model_and_write_db(model_id, username, qid, CMOs, scores):
    try:
        Helper.recordModelMetrics(identifier=model_id)  # Clear DB entries of records for this model
        _LOGGER.info("Metrics cleared for modelid={}, username={}".format(model_id, username))
        ExpertModelAPI().fit_unsupervised(model_id=model_id, data=Helper.CMOStore.models())
        _LOGGER.info("Model fit unsupervised completed for modelid={}, username={}".format(model_id, username))
        metrics = ExpertModelAPI().partial_fit(model_id=model_id, data=CMOs, targets=scores)
        _LOGGER.info("Model fit supervised completed for modelid={}, username={}".format(model_id, username))
        Helper.recordModelMetrics(identifier=model_id, metrics=metrics)
        _LOGGER.info("Metrics written to DB for modelid={}, username={}".format(model_id, username))
        db.execute("submitBatch", [username, qid])  # Update batch assignment
    except Exception as e:
        print(str(e))
        # An error has occured within the ML backend
        raise exc.HTTPBadRequest("Error on learning batch")


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

    def add_process(self, fn, *args, **kwargs):
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


@view_config(route_name="submitBatch", renderer="json")
def submitBatch(request):
    permissions(request)

    try:
        qid = int(request.params["qid"])
    except KeyError as e:
        raise exc.HTTPBadRequest("Question ID not passed")

    username = request.session["username"]

    # Collect Expert information
    expert = db.executeOne("collectEMIdentifier", [username, qid])
    batch = db.execute("collectBatch", [username, qid])

    # Prepare batch information
    CMOs, scores = [], []
    for CMOid, score in batch:
        CMOs.append(ClimateModelOutput.load(os.path.join(CMOSTORAGE + str(CMOid))))
        scores.append(score)

    # Train the expert model
    ProcessRunner().add_process(fit_model_and_write_db, expert["identifier"], username, qid, CMOs, scores)

    return {}


@view_config(route_name="removeBatch", renderer="json")
def removeBatch(request):
    permissions(request)

    try:
        qid = int(request.params["qid"])
    except KeyError as e:
        raise exc.HTTPBadRequest("Question ID not passed")

    db.execute("deleteBatch", [request.session["username"], qid])

    return {}
