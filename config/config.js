/* Config Sample
 *
 * For more information on how you can configure this file
 * see https://docs.magicmirror.builders/configuration/introduction.html
 * and https://docs.magicmirror.builders/modules/configuration.html
 *
 * You can use environment variables using a `config.js.template` file instead of `config.js`
 * which will be converted to `config.js` while starting. For more information
 * see https://docs.magicmirror.builders/configuration/introduction.html#enviromnent-variables
 */
let config = {
	address: "localhost", // Address to listen on, can be:
	// - "localhost", "127.0.0.1", "::1" to listen on loopback interface
	// - another specific IPv4/6 to listen on a specific interface
	// - "0.0.0.0", "::" to listen on any interface
	// Default, when address config is left out or empty, is "localhost"
	port: 8080,
	basePath: "/", // The URL path where MagicMirror² is hosted. If you are using a Reverse proxy
	// you must set the sub path here. basePath must end with a /
	ipWhitelist: ["127.0.0.1", "::ffff:127.0.0.1", "::1"], // Set [] to allow all IP addresses
	// or add a specific IPv4 of 192.168.1.5 :
	// ["127.0.0.1", "::ffff:127.0.0.1", "::1", "::ffff:192.168.1.5"],
	// or IPv4 range of 192.168.3.0 --> 192.168.3.15 use CIDR format :
	// ["127.0.0.1", "::ffff:127.0.0.1", "::1", "::ffff:192.168.3.0/28"],

	useHttps: false, // Support HTTPS or not, default "false" will use HTTP
	httpsPrivateKey: "", // HTTPS private key path, only require when useHttps is true
	httpsCertificate: "", // HTTPS Certificate path, only require when useHttps is true

	language: "en",
	locale: "en-IN", // this variable is provided as a consistent location
	// it is currently only used by 3rd party modules. no MagicMirror code uses this value
	// as we have no usage, we  have no constraints on what this field holds
	// see https://en.wikipedia.org/wiki/Locale_(computer_software) for the possibilities

	logLevel: ["INFO", "LOG", "WARN", "ERROR"], // Add "DEBUG" for even more logging
	timeFormat: 12,
	units: "metric",

	modules: [
		{
			module: "alert"
		},
		{
			module: "updatenotification",
			position: "top_bar"
		},
		{
			module: "clock",
			position: "top_left"
		},
		{
			module: "compliments",
			position: "bottom_bar"
		},
		{
			module: "calendar",
			header: "Indian Public Holidays",
			position: "top_left",
			config: {
				calendars: [
					{
						symbol: "calendar-check",
						url: "https://calendar.google.com/calendar/ical/en.indian%23holiday%40group.v.calendar.google.com/public/basic.ics"
					}
				]
			}
		},
		{
			module: "MMM-WorkoutAssistant",
			position: "middle_center",
			config: {
				cameraIndex: 0, // Try different indices if needed
				exerciseType: "Automatic Detection" // Or specify an exercise
			}
		},
		/*
		{
			module: "MMM-AccuWeatherForecastDeluxe",
			header: "Tiled Layouts",
			position: "top_right",
			classes: "default everyone",
			disabled: false,
			config: {
				apikey: "CkK7js2DALpsU6AbBKe5MPYy335f9O6l",
				locationKey: "204108",
				hourlyForecastInterval: 2,
				maxDailiesToShow: 3,
				ignoreToday: true,
				showDayAsTomorrowInDailyForecast: true,
				showPrecipitationProbability: false,
				iconset: "4c",
				label_high: "",
				label_low: ""
			}
		},*/
		{
			module: "newsfeed",
			position: "bottom_bar",
			config: {
				feeds: [
					{
						title: "TOI Top Stories",
						url: "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
					},
					{
						title: "TOI World",
						url: "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms"
					},
					{
						title: "TOI Sports",
						url: "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms"
					}
				],
				showSourceTitle: true,
				showPublishDate: true,
				broadcastNewsFeeds: true,
				broadcastNewsUpdates: true,
				updateInterval: 300000, // refresh every 5 min
				reloadInterval: 600000 // reload feed every 10 min
			}
		},
		{
			module: "MMM-Jast",
			position: "bottom_left", // This can be any of the regions.
			config: {
				currencyStyle: "code", // One of ["code", "symbol", "name"]
				fadeSpeedInSeconds: 3.5,
				lastUpdateFormat: "HH:mm",
				maxChangeAge: 1 * 24 * 60 * 60 * 1000,
				maxWidth: "100%",
				numberDecimalsPercentages: 1,
				numberDecimalsValues: 2,
				displayMode: "vertical", // One of ["none", "vertical", "horizontal", "table"]
				showColors: true,
				showCurrency: true,
				showChangePercent: true,
				showChangeValue: false,
				showChangeValueCurrency: false,
				showHiddenStocks: false,
				showLastUpdate: false,
				showPortfolioValue: false,
				showPortfolioGrowthPercent: false,
				showPortfolioGrowth: false,
				showPortfolioPerformanceValue: false,
				showPortfolioPerformancePercent: false,
				showStockPerformanceValue: false,
				showStockPerformanceValueSum: false,
				showStockPerformancePercent: false,
				stocksPerPage: 2, // Only relevant for display mode "table"
				updateIntervalInSeconds: 300,
				useGrouping: false,
				virtualHorizontalMultiplier: 2,
				stocks: [
					{ name: "BASF", symbol: "BAS.DE", quantity: 10, purchasePrice: 70.4 },
					{ name: "SAP", symbol: "SAP.DE", quantity: 15, purchasePrice: 90.3 },
					{ name: "Henkel", symbol: "HEN3.DE", hidden: true },
					{ name: "Bitcoin", symbol: "BTC-EUR" }
				]
			}
		},
		{
			module: "MMM-SoccerLiveScore",
			position: "top_right", // This can be any of the regions.
			header: "Live-Scores",
			config: {
				leagues: [2019, 2021, 2000],
				displayTime: 2 * 60 * 1000,
				requestInterval: 6 * 60 * 1000, // 6 mins
				showNames: true,
				showLogos: true,
				showStandings: true,
				showTables: true,
				showScorers: true,
				scrollVertical: true,
				logostToInvert: [109], // some teams logo are not visible on dark background
				token: ["a97eac84a09348fd908e4622a0631b60"],
				requestsAvailablePerMinute: [10] // varies with subscription type to https://www.football-data.org/pricing
			}
		}
		/*{
			module: "MMM-GoogleTTS", // no `position` is needed.
			config: {
				welcome: ["May the force be with you", "Live long and prosper"],
				// String or Array of String or callback function to return String or Array. To disable this feature, set to null.
				/* Other example
    welcome: null,
    welcome: "Hello",
    welcome: ()=> {
      var d = Math.floor((Math.random() * 10) + 1)
      return "Today's Lucky number is" + d
    },

				dailyCharLimit: 129000,
				// 4 Million divide by 30. I think it's enough for daily usage. If you have a will to pay, you can expand this value as your wish. But free usage will be enough.
				// Warning. When you use WaveNet voice, your free quota will be `1 Million per month` not `4 Million`.

				sourceType: "text",
				// "text" or "ssml".

				voiceName: "en-US-Standard-C",
				// If exists. e.g)"en-US-Standard-C". You can select specific voice name when there are many voices with same languageCode and gender.
				// voiceName should be matched with languageCode and ssmlGender

				languageCode: "en-US",
				ssmlGender: "FEMALE",
				// "MALE", "FEMALE", "NEUTRAL" or "SSML_VOICE_GENDER_UNSPECIFIED"
				// supported voices, languages and gender;
				// https://cloud.google.com/text-to-speech/docs/voices

				playCommand: "aplay %OUTPUTFILE%",
				// aplay, mpg321, afplay, as your wish....
				// sometimes you should give more options to play correctly.
				// e.g) "aplay -D plughw:1,0 $OUTPUTFILE%"

				audioEncoding: "LINEAR16",
				// LINEAR16 (.wav) or MP3 (.mp3) for playCommand. You don't need to modify this when you use `aplay`

				notificationTrigger: {
					TEST_TTS: "Test TTS notification is coming",
					SHOW_ALERT: (payload, sender) => {
						return payload.message;
					}
				},
				// You can hook specific notification to speak something. String or callback function could be available.

				// You don't need to modify belows;
				notifications: {
					TTS_SAY: "TTS_SAY",
					TTS_SAY_STARTING: "TTS_SAY_STARTING",
					TTS_SAY_ENDING: "TTS_SAY_ENDING",
					TTS_SAY_ERROR: "TTS_SAY_ERROR"
				},
				credentialPath: "credentials.json"
			}
		}*/
	]
};

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== "undefined") {
	module.exports = config;
}
