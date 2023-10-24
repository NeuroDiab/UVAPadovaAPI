import requests
from flask import Flask, Response, request
from http import HTTPStatus
from AAPSHandler import AAPSHandler

server = Flask(__name__)

handler_instance = AAPSHandler()


@server.route('/')
def index():
    return Response("The server refuses the attempt to brew coffee with a teapot.", 418)

@server.route('/', methods=["POST"])
def checkServerStatus():
    return Response("", HTTPStatus.OK)

@server.route('/initialize', methods=["POST"])
def initializeSimulation():
    return Response("InitrQuest", HTTPStatus.OK)


@server.route('/add', methods=["POST"])
def dosingInsulin():
    return Response("", HTTPStatus.OK)


@server.route('/getBG', methods=["POST"])
def requestBloodGlucose():
    result, status = handler_instance.getBloodGlucose()
    if status is not None:
        return Response(result, HTTPStatus.OK)
    else:
        return Response(result, HTTPStatus.BAD_REQUEST)




server.run(host="0.0.0.0", port=5001)