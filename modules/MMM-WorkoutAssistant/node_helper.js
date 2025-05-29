const NodeHelper = require("node_helper");
const { PythonShell } = require("python-shell");
const path = require("path");
const os = require("os");

module.exports = NodeHelper.create({
	start: function () {
		this.pythonProcess = null;
	},

	socketNotificationReceived: function (notification, payload) {
		if (notification === "INIT") {
			this.initializeBackend(payload);
		}
	},

	initializeBackend: function (config) {
		// Kill existing process if any
		if (this.pythonProcess) {
			this.pythonProcess.kill();
		}

		// Dynamically set pythonPath depending on OS
		let pythonPath = "python3"; // default for macOS/Linux
		if (os.platform() === "win32") {
			pythonPath = path.join(__dirname, "..", "..", "venv", "Scripts", "python.exe");
		} else {
			pythonPath = pythonPath = "/Users/adithyan/Downloads/Magic_Mirror/venv/bin/python3";
		}

		const options = {
			mode: "json",
			pythonPath: pythonPath,
			scriptPath: path.join(__dirname, "workout_backend"),
			args: ["--camera_index", config.cameraIndex, "--exercise_type", config.exerciseType]
		};

		this.pythonProcess = new PythonShell("app.py", options);

		this.pythonProcess.on("message", (message) => {
			this.sendSocketNotification(message.type, message.payload);
		});

		this.pythonProcess.on("stderr", (stderr) => {
			console.error("Python STDERR:", stderr);
		});

		this.pythonProcess.on("error", (error) => {
			console.error("Python Error:", error);
			this.sendSocketNotification("ERROR", { message: error.toString() });
		});

		this.pythonProcess.on("close", () => {
			console.log("Python process closed");
		});
	},

	stop: function () {
		if (this.pythonProcess) {
			this.pythonProcess.kill();
		}
	}
});
