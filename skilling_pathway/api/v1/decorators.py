from flask import current_app
import requests
from flask import request, g
import os
from skilling_pathway.api.config import config

def handle_response(func):
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            # print(response)
            data, status, *args = response
            if data["type"] == "custom_error":
                if "data" not in data:
                    data["data"] = {}
            elif data["type"] == "validation_error":
                # added for handling invalid screen types or
                # others if using validation_error type
                # if 'data' not in data:
                #     data['data'] = {}
                # else:
                if type(data["message"]) == str:
                    if "data" not in data:
                        data["data"] = {}
                elif type(data["message"]) == dict:
                    data["data"] = data["message"]

                    # process the data
                    message = (
                        "Request cannot be processed due to invalid fields : "
                    )
                    for key, value in data["data"].items():
                        message += key + ", "
                    message = message[:-2]  # remove trailing comma
                    data["message"] = message
                else:
                    pass  # can be processed for different types of data

            elif data["type"] == "success_message":
                if "data" not in data:
                    data["data"] = {}

            elif data["type"] == "success_data":
                if "message" not in data:
                    data["message"] = ""

            elif data["type"] == "authentication_error":
                data["data"] = {}

            return data, status
        except KeyError:
            return data, status
        except Exception as e:
            # current_app.error_logger.error("validation error", exc_info=e)
            data = {
                "message": "Something went wrong, please try after some time",
                "type": "custom_error",
                "data": {},
                "status": False,
            }
            return data, 400

    apidoc = getattr(func, "__apidoc__", {})
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.__apidoc__ = apidoc
    return wrapper



def authenticate(func):
    def wrapper(*args, **kwargs):
        try:
            access_token = request.headers.get("access-token")
            secret_key = request.headers.get("secret-key")

            if access_token:
                header = {
                    "Authorization": "Bearer " + access_token,
                    "Content-Type": "application/json",
                }
                try:
                    validate_user = requests.request(
                        "GET", config.uim_verify_token_url, headers=header
                    ).json()
                    print(validate_user)
                    if validate_user.get("status"):
                        # set user id to request object
                        setattr(request, "user", validate_user["data"]["sub"])
                        setattr(g, "user_uuid", validate_user["data"]["sub"])
                        setattr(
                            request,
                            "group",
                            validate_user["data"].get("group"),
                        )
                        setattr(request, "full_name",
                                validate_user["data"]["full_name"])
                    else:
                        return (
                            {
                                "message": "Invalid access token",
                                "type": "authentication_error",
                                "status": False,
                            },
                            401,
                        )
                except Exception as e:
                    return (
                        {
                            "message": str(e),
                            "type": "custom_error",
                            "status": False,
                        },
                        400,
                    )

                return func(*args, **kwargs)

            elif secret_key:
                if secret_key != os.environ.get("SERVER_SECRET"):
                    return (
                        {
                            "message": "Invalid secret key",
                            "type": "authentication_error",
                            "status": False,
                        },
                        401,
                    )
                setattr(request, "service_call", True)
                return func(*args, **kwargs)
            else:
                return (
                    {
                        "message": "Either access token or secret key is"
                        " required",
                        "type": "authentication_error",
                        "status": False,
                    },
                    400,
                )
        except KeyError:
            return (
                {
                    "message": " 'access-token' is missing in headers",
                    "type": "authentication_error",
                    "status": False,
                },
                401,
            )
        except Exception as e:
            return {"message": str(e)}

    apidoc = getattr(func, "__apidoc__", {"expect": []})
    wrapper.__apidoc__ = apidoc
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper