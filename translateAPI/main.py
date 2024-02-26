import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
import argostranslate.package
import argostranslate.translate
import json
from firebase_admin import auth, credentials, initialize_app
import jwt
from dotenv import load_dotenv
load_dotenv()

server_url = os.getenv('SERVER_URL_PROD') if os.getenv(
    'ENVIRONMENT') == 'PROD' else os.getenv('SERVER_URL_DEV')
app = Flask(__name__)

# cors = CORS(app, resources={
#             r"/translate/*": {"origins": server_url}})
# Initialize Firebase
cred = credentials.Certificate(
    'ryu-chat-f1c33-firebase-adminsdk-xvfhf-9af6c0bcb9.json')
firebase = initialize_app(cred)


def getPackage(from_code, to_code):
    # Returns a package
    try:
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
            )
        )
        return package_to_install
    except Exception as e:
        print(f'getPackage Exception: {e}')
        return []


def downloadPackage(from_code, to_code):
    try:
        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
            )
        )
        argostranslate.package.install_from_path(package_to_install.download())
        return "got index"
    except Exception as e:
        return "failed to get index"


# @app.before_request
# @cross_origin(origins=[server_url], automatic_options=True)
def authenticateToken(request):
    try:
        # id_token = request.get_json()["idToken"]
        token = request.get_json()["accessToken"]
        # decoded_token = auth.verify_id_token(token)
        # print(decoded_token)
        decoded_jwt = jwt.decode(token, os.getenv(
            "ACCESS_TOKEN_SECRET"), algorithms="HS256", audience="Service #3")
        print(decoded_jwt)
        if (decoded_jwt.get("isStillSubcribed") and decoded_jwt.get("tier") > 0):
            return {"status": "authorized"}
        else:
            return {"status": "unauthorized", "message": "Subscribe to use this feature."}
    except Exception as error:
        print(error)
        return {"status": "error", "translation": "", "message": f'Issue while authenticating user: {error}'}


@app.route("/", methods=["GET"])
def getIndex():
    return render_template("index.html"), 200


@app.route("/status", methods=["GET"])
# @cross_origin(methods=['GET'], allow_headers=['Access-Control-Allow-Origin'])
def getStatus():
    status = ""
    text = "Some Test: Success"
    from_code = "en"
    to_code = "es"

    try:
        installed_packages = argostranslate.package.get_installed_packages()
        package = getPackage(from_code, to_code)
        if package:
            if package not in installed_packages:
                argostranslate.package.install_from_path(
                    package.download())

            convertedText = argostranslate.translate.translate(
                text, from_code, to_code)
        status = convertedText
    except Exception as error:
        status = error

    return render_template('success.html', status=status)


@app.route("/updateIndex", methods=["GET"])
# @cross_origin(origins=['https://www.matiechat.com', 'https://matiechat.com'], methods=['GET'], allow_headers=['Access-Control-Allow-Origin'])
def updateIndex():
    from_code = request.args.get("from_code")
    to_code = request.args.get("to_code")
    if (not from_code or not to_code):
        return "Missin language codes [from_code,to_code]", 400

    downloadPackage(from_code, to_code)
    return "updated package index", 201


@app.route("/translate", methods=["POST"])
@cross_origin(origins=[server_url], automatic_options=True, methods=['POST', 'OPTIONS'], allow_headers=['Content-Type'])
def translate():
    data = request.get_json()["data"]
    from_code = data["from_code"]
    to_code = data["to_code"]
    text = data["text"]
    result = authenticateToken(request)

    if (not from_code or not to_code or not text or text == ''):
        return jsonify({"translation": "", "message": "Missin language code or text to translate."}), 400
    if (result.get('status') == "error" or result.get('status') == 'unauthorized'):
        return jsonify({"translation": "", "message": result.get('message')}), 400

    try:
        installed_packages = argostranslate.package.get_installed_packages()
        package = getPackage(from_code, to_code)
        print(f'installed_packages: {installed_packages}')
        # Translate
        if package:
            if package not in installed_packages:
                argostranslate.package.install_from_path(package.download())
        else:
            raise Exception(
                f'Get Package Exception: package for {from_code} -> {to_code} does not exist')

        translatedText = argostranslate.translate.translate(
            text, from_code, to_code)
        return jsonify({"translation": translatedText}), 200

    except Exception as error:
        print(error)
        try:
            package = getPackage(from_code, "en")

            if package:
                if package not in installed_packages:
                    argostranslate.package.install_from_path(
                        package.download())

                convertedText = argostranslate.translate.translate(
                    text, from_code, "en")
                if to_code == "en":
                    return jsonify({"translation": convertedText}), 201

            package = getPackage("en", to_code)
            if package:
                if package not in installed_packages:
                    argostranslate.package.install_from_path(
                        package.download())

                translatedText = argostranslate.translate.translate(
                    convertedText, "en", to_code)
                return jsonify({"translation": translatedText}), 201
            return jsonify({"translation": f'could not translate {from_code} -> {to_code}'}, 400)
        except Exception as error:
            print(error)
            return jsonify({"translation": f'Error while attempting to translate from {from_code} -> {to_code}'}), 500


if __name__ == "__main__":
    try:
        print(server_url)
        app.run(port=8000, debug=True)
    except Exception as error:
        print(error)
        print("Error while initializing translate Engine")
