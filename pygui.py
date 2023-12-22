"""
    PyGUI library
"""
import os  # Os for path stuff
from enum import Enum  # Enum for enums
from typing import Callable, List  # Used for type hinting
import flask  # Flask web framework
from gevent.pywsgi import WSGIServer  # WSGI server for Flask
import discord  # Needed for the bot. REPLACE THIS WITH THE LIBRARY YOU USE IF IT DIFFERS!!
import secrets  # Needed for flask session
import json  # Needed for the Settings class


class Status(Enum):
    """
    Status codes for notifications
    """

    SUCCESS = 0
    ERROR = 1
    WARNING = 2
    FATAL = 3


class WidgetType(Enum):
    """
    Settings widget types that will be rendered.
    """

    BOOLEAN = 0
    NUMBER_FIELD = 1
    NUMBER_SLIDER = 2
    STRING = 3
    RADIO_BUTTON = 4


class Setting:
    """
    This class represents a setting.
    """

    def __init__(self, wtype: WidgetType, name: str, value, options: List[str] = []):
        self.wtype = wtype
        self.name = name
        self.value = value
        self.options = options  # This is only used when wtype is RADIO_BUTTON (4)


class Settings:
    """
    This class represents a collection of settings.
    """

    def __init__(self, settings: List[Setting] = [], filename: str = "settings.json"):
        """
        Initializes the object with a list of settings and a filename.

        Args:
            settings (List[Setting], optional): A list of Setting objects representing the settings. Defaults to [].
            filename (str, optional): The name of the file to save the settings to. Defaults to "settings.json".

        Returns:
            None
        """
        self.settings = settings
        self.filename = filename
        self.blackistedSettings = ["token"]

        # Try to open the provided filename and read the settings from it
        if self.filename not in os.listdir():
            self.initConfig()
            return

        if len(self.settings) != 0:
            return

        with open(filename, "r") as f:
            # Convert contents to json
            fileJson = json.load(f)
            for setting in fileJson:
                if setting in self.blackistedSettings:
                    continue
                if (
                    "type" not in fileJson[setting]
                    or "value" not in fileJson[setting]
                    or "options" not in fileJson[setting]
                ):
                    raise Exception("Malformed settings file")
                self.settings.append(
                    Setting(
                        WidgetType(fileJson[setting]["type"]),
                        setting,
                        fileJson[setting]["value"],
                        fileJson[setting]["options"],
                    )
                )

    def initConfig(self) -> None:
        if len(self.settings) != 0:
            with open(self.filename, "w") as f:
                # Convert self.settings into a dict which we can turn to a json later
                settings_as_dict = {}
                for setting in self.settings:
                    settings_as_dict[setting.name] = {
                        "type": setting.wtype.value,
                        "value": setting.value,
                        "options": setting.options,
                    }
                jsoned_dict = json.dumps(settings_as_dict)
                f.write(jsoned_dict)
        else:
            print("[FATAL] No settings file found and no templates given")
            exit(1)

    def get(self, name) -> Setting | None:
        """
        Finds and returns the setting object with the given name.

        Parameters:
            name (str): The name of the setting to search for.

        Returns:
            Setting or None: The setting object with the given name, or None if no such setting exists.
        """
        for setting in self.settings:
            if setting.name == name:
                return setting
        return None

    def set(self, name, value):
        """
        Set the value of a setting in the object.

        Parameters:
            name (str): The name of the setting to be set.
            value (Any): The value to be assigned to the setting.

        Raises:
            AttributeError: If the setting does not exist.

        Returns:
            None
        """
        for setting in self.settings:
            if setting.name == name:
                # print("Found... setting value")
                if (
                    setting.wtype == WidgetType.NUMBER_FIELD
                    or setting.wtype == WidgetType.NUMBER_SLIDER
                ):
                    try:
                        # Try convert the value into a float
                        float(value)
                    except:
                        raise AttributeError(
                            f"{value} is not a number. Changing types aren't allowed!"
                        )
                elif setting.wtype == WidgetType.RADIO_BUTTON:
                    if value not in setting.options:
                        raise AttributeError(f"{value} is not a valid option")
                setting.value = value
                try:
                    filejson = None
                    with open(self.filename, "r") as f:
                        filejson = json.load(f)
                    filejson[setting.name]["value"] = value
                    # print(filejson[setting.name])
                    # exit(1)
                    with open(self.filename, "w") as f:
                        jsoned_dict = json.dumps(filejson)
                        f.write(jsoned_dict)
                    return
                except FileNotFoundError:
                    print("FATAL: Settings file not found")
                    exit(1)
                except Exception as e:
                    raise e

        raise AttributeError(
            f"The {name} setting does not exist. In the object {self.__class__.__name__}"
        )


class Message:
    """
    This class represents a notification in the GUI.
    """

    def __init__(self, content: str, status: Status):
        self.content = content
        self.status = status.name

    # Show as a dict
    def as_dict(self):
        return {"content": self.content, "status": self.status}


class Window:
    """
    Represents the whole GUI and its internal components
    """

    def __init__(
        self,
        bot: discord.Client,
        bot_name: str,
        password: str,
        functions: dict[str, Callable],
        settings: Settings,
    ):
        self.server = flask.Flask(__name__)
        self.bot = bot
        self.password = password
        self.botname = bot_name
        self.functions = functions
        self.settings = settings

    def register(self):
        """
        Register routes and decorators for the Flask server.

        Returns:
            None
        """

        self.server.secret_key = secrets.token_hex()

        @self.server.route("/")
        def index():
            return flask.render_template(
                "index.html",
                name=self.bot.user.name,
                sbname=self.botname,
                servers=self.bot.guilds.__len__(),
                friends=self.bot.user.friends.__len__(),
                validpass=self.password == flask.session.get("password"),
            )

        self.server.static_folder = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "static"
        )

        @self.server.route("/settings")
        def settings():
            if (
                flask.session.get("password") is None
                or flask.session.get("password") != self.password
            ):
                return flask.redirect("/")
            return flask.render_template(
                "settings.html",
                WidgetType=WidgetType,
                settings=self.settings,
                sess=flask.session["password"],
                sbname=self.botname,
            )

        @self.server.route("/functions")
        def functions():
            return flask.render_template("functions.html", sbname=self.botname)

        @self.server.post("/validate")
        def validate():
            body = flask.request.get_data().decode()
            data: dict = json.loads(body)
            if data.get("password") is None or data.get("password") != self.password:
                return Message("Invalid password", Status.FATAL).as_dict()
            session = flask.session
            session["password"] = data["password"]
            return Message("Valid", Status.SUCCESS).as_dict()

        @self.server.post("/api/function/<function>")
        def apiFunc(function: str):
            body = flask.request.get_data().decode()
            # print(body)
            data: dict = json.loads(body)
            if data.get("password") is None or data.get("password") != self.password:
                return Message("Invalid password", Status.FATAL).as_dict()
            if function not in self.functions:
                return Message("Function not found", Status.ERROR).as_dict()
            function_obj = self.functions[function]
            if function_obj.__code__.co_argcount != len(data) - 1:
                return Message("Invalid number of arguments", Status.ERROR).as_dict()
            if function_obj.__code__.co_argcount == 0:
                return flask.render_template_string(function_obj().__str__())
            else:
                data.pop("password")
                return flask.render_template_string(
                    function_obj(*data.values().__str__())
                )

        @self.server.post("/api/setting/get/<setting_name>")
        def api_setting_get(setting_name: str):
            body = flask.request.get_data().decode()
            data: dict = json.loads(body)
            if data.get("password") is None or data.get("password") != self.password:
                return Message("Invalid password", Status.FATAL).as_dict()

            setting = self.settings.get(setting_name)
            if setting is None:
                return Message("Setting not found", Status.ERROR).as_dict()
            return flask.render_template_string(str(setting.value))

        @self.server.post("/api/setting/set/<setting_name>")
        def api_setting_set(setting_name: str):
            body = flask.request.get_data().decode()
            data: dict = json.loads(body)
            if data.get("password") is None or data.get("password") != self.password:
                return Message("Invalid password", Status.FATAL).as_dict()
            setting = self.settings.get(setting_name)
            if setting is None:
                return Message("Setting not found", Status.ERROR).as_dict()
            if data["value"] is None:
                return Message("No value is provided", Status.ERROR).as_dict()
            try:
                self.settings.set(setting.name, data["value"])
            except AttributeError as e:
                return Message(str(e), Status.ERROR).as_dict()
            # print("Updated")
            return Message("Setting updated", Status.SUCCESS).as_dict()

        @self.server.errorhandler(404)
        def page_not_found(e):
            return flask.render_template("404.html"), 404

    def run(self):
        """
        Run the server.

        This method starts the HTTP server and makes it listen for incoming requests on the specified IP address and port.
        The server instance is created using the provided WSGI application.

        :param self: The current instance of the class.
        :return: None
        """
        http_server = WSGIServer(("127.0.0.1", 8080), self.server, log=None)
        http_server.serve_forever()
