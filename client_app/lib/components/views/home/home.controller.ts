import * as ng from 'angular';
import * as lodash from 'lodash';

class HomeController implements ng.IComponentController{
	public socket : WebSocket;
	public socketActive : boolean;
	public text : string;
	public textList : any;
	public hasStarted : boolean;
	public progressDict : Array<any>;
	public marker : number;

	constructor(public $scope : ng.IScope){
		// URL for the websocket connection
		const socketUrl = 'ws://0.0.0.0:8080';
		this.socketActive = false;

		// Initalize test text
		this.text = 'I like to eat cheeseburgers and play with my friends outside. We do cool stuff man.'
		this.hasStarted = false;
		this.textList = [];
		this.marker = 0;
		this.progressDict = [];

		// Init websocket
		this.socket = new WebSocket(socketUrl);
		this.socket.addEventListener('open', () => this.socketActive = true);

		// Add respective events to the websockets
		this.addEvents(this.socket);
	}

	addEvents(socket : WebSocket){
		/* Add respective events to the websockets */
		socket.addEventListener('message', (message : string) => {
			const output = JSON.parse(message.data);
			this.progressDict = output.text;
			this.marker = output.marker;
			this.$scope.$apply();
		});
	}

	wsMessage(message : string){
		const output = JSON.parse(message.data);

		console.log(message, output);

		this.progressDict = output.text;
		this.marker = output.marker;
	}

	textToMap(text : string) : any{
		return text.split(' ');
	}

	convertFloat32ToInt16(buffer){
		/* Convert the float32 to a 16bit int */

		// TBH I copied this from a tutorial
		const l = buffer.length;
	  const buf = new Int16Array(l);
	  while (l--) {
	    buf[l] = Math.min(1, buffer[l])*0x7FFF;
	  }

	  return buf.buffer;
	} 

	startAudioStream(){
		/* Function to initialize streaming audio from the client to the server */
		this.hasStarted = true;
		this.textList = this.textToMap(this.text);

		// Socket must be open
		if (!this.socketActive){
			return;
		}

		// Set audio object
		this.socket.send(this.text);

		// Create the stream
		window.navigator.getUserMedia({audio: true, video: false}, (stream) => {

			// Set up audio context object
			const context = new AudioContext();

			const audioInput = context.createMediaStreamSource(stream);

			// Create script processor which will send data to the websocket
			const bufferSize = 16384;
			const recorder = context.createScriptProcessor(bufferSize, 1, 1);

			recorder.onaudioprocess = (event) => {
				// Only getting the left channel data, may want to change
				const left = event.inputBuffer.getChannelData(0);

				// Convert the int16 and send
				this.socket.send(this.convertFloat32ToInt16(left));
			}

			audioInput.connect(recorder);
			recorder.connect(context.destination);

		}, (error) => console.error(error));
	}

	getClass(index){
		// Get the corresponding classname from the index of a word
		if (index == this.marker){
			return 'marker';
		}

		if (index > this.marker){
			return '';
		}

		const item = lodash.find(this.progressDict, {index: index});

		return item.correct ? 'correct' : 'incorrect';
	}
}

HomeController.$inject = ['$scope'];

export default HomeController;