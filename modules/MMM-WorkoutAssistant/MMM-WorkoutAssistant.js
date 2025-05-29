Module.register("MMM-WorkoutAssistant", {
	defaults: {
		cameraIndex: 0,
		exerciseType: "Automatic Detection",
		showFeedback: true,
		showStats: true
	},

	start: function () {
		this.repCount = 0;
		this.startTime = new Date();
		this.feedback = [];
		this.currentExercise = "None detected";
		this.videoUrl = null;
		this.stats = { calories: 0, repsPerMin: 0 };

		// Send initialization message to node helper
		this.sendSocketNotification("INIT", this.config);
	},

	getDom: function () {
		const wrapper = document.createElement("div");
		wrapper.className = "workout-wrapper";

		// Title
		const title = document.createElement("h2");
		title.innerHTML = "Workout Assistant";
		wrapper.appendChild(title);

		// Video feed container
		this.videoContainer = document.createElement("div");
		this.videoContainer.className = "video-container";
		if (this.videoUrl) {
			const video = document.createElement("img");
			video.src = this.videoUrl;
			video.className = "workout-video";
			this.videoContainer.appendChild(video);
		} else {
			this.videoContainer.innerHTML = "Loading camera feed...";
		}
		wrapper.appendChild(this.videoContainer);

		// Stats row
		if (this.config.showStats) {
			const statsRow = document.createElement("div");
			statsRow.className = "stats-row";

			const repCount = document.createElement("div");
			repCount.className = "stat-box";
			repCount.innerHTML = `<strong>Reps:</strong> ${this.repCount}`;
			statsRow.appendChild(repCount);

			const exercise = document.createElement("div");
			exercise.className = "stat-box";
			exercise.innerHTML = `<strong>Exercise:</strong> ${this.currentExercise}`;
			statsRow.appendChild(exercise);

			const elapsed = Math.floor((new Date() - this.startTime) / 1000);
			const timeStr = `${Math.floor(elapsed / 60)}:${(elapsed % 60).toString().padStart(2, "0")}`;
			const time = document.createElement("div");
			time.className = "stat-box";
			time.innerHTML = `<strong>Time:</strong> ${timeStr}`;
			statsRow.appendChild(time);

			wrapper.appendChild(statsRow);
		}

		// Feedback
		if (this.config.showFeedback && this.feedback.length > 0) {
			const feedbackTitle = document.createElement("h3");
			feedbackTitle.innerHTML = "Form Feedback:";
			wrapper.appendChild(feedbackTitle);

			const feedbackList = document.createElement("ul");
			feedbackList.className = "feedback-list";
			this.feedback.slice(-3).forEach((fb) => {
				const item = document.createElement("li");
				item.innerHTML = fb;
				feedbackList.appendChild(item);
			});
			wrapper.appendChild(feedbackList);
		}

		return wrapper;
	},

	socketNotificationReceived: function (notification, payload) {
		switch (notification) {
			case "VIDEO_FRAME":
				this.videoUrl = payload.frame;
				this.repCount = payload.repCount;
				this.currentExercise = payload.exercise;
				this.feedback = payload.feedback || [];
				this.stats = payload.stats || { calories: 0, repsPerMin: 0 };
				this.updateDom();
				break;

			case "STATUS":
				Log.info(`Workout Assistant: ${payload.message}`);
				break;

			case "ERROR":
				Log.error(`Workout Assistant Error: ${payload.message}`);
				this.videoContainer.innerHTML = `<div style="color: red;">Error: ${payload.message}</div>`;
				break;
		}
	},
	getStyles: function () {
		return ["MMM-WorkoutAssistant.css"];
	}
});
